import bpy
import bmesh
import mathutils

import pyclipper

import numpy as np
import math

from .visHullTwoD import Scene, MyPolygon



class PointCreator:
    def __init__(self):
        print("Creating PointCreator")


    # "Island"-finding modified from an answer by user batFinger 
    # on Blender StackExchange submitted 2018-03-28 in response to the
    # question "How to find the number of loose parts with Blender's Python API?"
    # asked by user Tim Ayres on 2017-03-10. Link to the answer:
    # https://blender.stackexchange.com/a/105142
    # The question has also been web archived at:
    # http://web.archive.org/web/20210426010446/https://blender.stackexchange.com/questions/75332/how-to-find-the-number-of-loose-parts-with-blenders-python-api

    # Here, we find all vertices in the same "connected component" as vert
    # and we update the list retVerts, passed in by reference and
    # updated via "side effects", to get the whole connected component.
    def _findIsland(self, v, retVerts):
        retVerts.append(v)
        
        adjVerts = [e.other_vert(v) for e in v.link_edges]


        v.tag = True
        
        for av in adjVerts:
            if not av.tag:
                self._findIsland(av, retVerts,)
        
        return retVerts

    # "Island"-finding modified from an answer by user batFinger 
    # on Blender StackExchange submitted 2018-03-28 in response to the
    # question "How to find the number of loose parts with Blender's Python API?"
    # asked by user Tim Ayres on 2017-03-10. Link to the answer:
    # https://blender.stackexchange.com/a/105142
    # The question has also been web archived at:
    # http://web.archive.org/web/20210426010446/https://blender.stackexchange.com/questions/75332/how-to-find-the-number-of-loose-parts-with-blenders-python-api
    def _getIslands(self, bm):
        retVal = []
        for v in bm.verts:
            v.tag = False
        verts = set(bm.verts)
        while verts:
            v = verts.pop()
            island = self._findIsland(v, [])
            retVal.append(island)
            verts -= set(island)
        for v in bm.verts:
            v.tag = False
        
        return retVal

    def _coord2D(self, changeOfBasis, planePoint, vert):
        vecOnPlane = (vert.co - planePoint)
        changedVec = changeOfBasis @ vecOnPlane
        return (changedVec.x, changedVec.y)

    def _diffAtan(self, fromCoord, toCoord):
        def atanPos(coord):
            regAtan = math.atan2(coord[1], coord[0])
            if regAtan < 0:
                regAtan += (2.0 * math.pi)
            return regAtan
        angle0 = atanPos(fromCoord)
        angle1 = atanPos(toCoord)
        
        if angle1 < angle0:
            angle1 += 2.0*math.pi
            
        return angle1 - angle0

    def getPoints(self):
        # Get the active mesh
        obj = bpy.context.object

        keepPolygons = []
        discardPolygons = []

        # 1. Make copy of mesh.
        meOrig = obj.data
        bmOrig = bmesh.new()
        bmOrig.from_mesh(meOrig)

        # 2. Perform a limit dissolve.
        r = bmesh.ops.dissolve_limit(bmOrig, angle_limit = 0.01, use_dissolve_boundaries = False, verts = bmOrig.verts, edges = bmOrig.edges)

        # 3. Now, for each face in the mesh, make ANOTHER copy of the whole mesh and continue.
        bmOrig.faces.ensure_lookup_table()
        for origFace in bmOrig.faces:
            bmCopy = bmOrig.copy()
            bmCopy.faces.ensure_lookup_table()
            faceToUse = bmCopy.faces[origFace.index]



            # 4. Bisect the copy with face.normal and with a coord of face.vertices[0].co
            planeNormal = faceToUse.normal.copy()
            planePoint = faceToUse.verts[0].co.copy()


            # First, we need to get two orthogonal vectors to use for the
            # "basis" of our 2D plane space.
            squaredLen = planeNormal.dot(planeNormal)
            if squaredLen != 1.0:
                planeNormal.normalize()

            # For our "x" basis vector, we just use the method for finding
            # perpendicular vectors in 2D.
            localX = mathutils.Vector((0.0, 0.0, 0.0))
            if abs(planeNormal.z - 1.0) < 0.1: # CHANGE THRESHOLD?
                localX.x = planeNormal.z
                localX.z = -planeNormal.x
            else:
                localX.x = planeNormal.y
                localX.y = -planeNormal.x
            localX.normalize()
            
            # Then for our "y" basis vector, we use a cross product.
            localY = planeNormal.cross(localX)
            localY.normalize()

            # Create the change-of-basis matrix.
            # In blender, matrices are created row-by-row. That is,
            # like "myMatrix = Matrix([topRow, middleRow, bottomRow])"
            changeOfBasis = mathutils.Matrix([localX, localY, planeNormal])

            geom = list(bmCopy.verts) + list(bmCopy.edges) + list(bmCopy.faces)
            r = bmesh.ops.bisect_plane(bmCopy, geom=geom, 
                plane_co=planePoint, plane_no=planeNormal,
                clear_outer = True, clear_inner = True)

            # 5. Delete the polygon corresponding to the original face.
            # (Also delete doubles to prevent other problems)
            bmesh.ops.delete(bmCopy, geom = [faceToUse], context='FACES')

            bmesh.ops.delete(bmCopy, geom = list(bmCopy.faces), context="FACES_ONLY")

            bmesh.ops.remove_doubles(bmCopy, verts = bmCopy.verts, dist = 0.0001)

            # 6. Get the set of all "polygons" that remain.
            islands = self._getIslands(bmCopy)

            # Create faces for the islands so that order and everything is 
            # definitely okay. We want to treat these as polygons, not as mere
            # sets of vertices.
            
            # Algorithm for getting the "outer polygon" from a bunch of
            # vertices and edges inspired by the answer by user CiaPan 
            # on StackOverflow submitted 2015-07-01 in response to the
            # question "Outermost Polygon from a set of Edges"
            # asked by user Charles Taylor on 2015-07-01. Link to the answer:
            # https://stackoverflow.com/a/31172403
            # The question has also been web archived at:
            # https://web.archive.org/web/20200722071633/https://stackoverflow.com/questions/31169125/outermost-polygon-from-a-set-of-edges
            
            islandVertCoordPairLists = []
            for isle in islands:        
                vertCoordDict = {}
                for v in isle:
                    vertCoordDict[v] = self._coord2D(changeOfBasis, planePoint, v)
                
                outerVerts = []
                outerEdges = []
                
                # Algorithm for outerVerts and outerEdges goes here!
                minVert = isle[0]
                for keyVert in vertCoordDict.keys():
                    if vertCoordDict[keyVert] < vertCoordDict[minVert]:
                        minVert = keyVert
                originalVert = minVert
                lastDir = (0, -1) # Downwards
                currentVert = minVert
                
                prevID = -1
                
                while currentVert != originalVert or len(outerVerts) == 0:
                    currentPos = vertCoordDict[currentVert]
                    currentEdge = None
                    minAngleDiff = 2.0 * math.pi
                    for e in currentVert.link_edges:
                        adjVert = e.other_vert(currentVert)
                        diffX = vertCoordDict[adjVert][0] - currentPos[0]
                        diffY = vertCoordDict[adjVert][1] - currentPos[1]
                        angleDiff = self._diffAtan(lastDir, (diffX, diffY))
                        if angleDiff < minAngleDiff and adjVert.index != prevID:
                            minAngleDiff = angleDiff
                            currentEdge = e
                    
                    newVert = currentEdge.other_vert(currentVert)
                    newPos = vertCoordDict[newVert]
                    lastDir = (newPos[0] - currentPos[0], newPos[1] - currentPos[1])
                    prevID = currentVert.index
                    currentVert = newVert
                    outerVerts.append(currentVert)
                    outerEdges.append(currentEdge)
                
                    
                bmesh.ops.contextual_create(bmCopy, geom = outerEdges)

            # 7. If anything remains (otherwise, just add orig face to "keep" mesh):
            if len(bmCopy.faces) > 0:
                '''
                print("OrigFace:")
                for origVert in origFace.verts:
                    print(" -", origVert.co)
                print("Islands ({0}):\n".format(len(islands)))
                for isleIndex in range(len(islands)):
                    print("  Isle {0}:".format(isleIndex))
                    for isleVert in islands[isleIndex][0]:
                        print("   -", isleVert.co)
                    print()
                '''
                # a) Project the result into the plane to get 2D coordinates.

                

                print("Num of islands:", len(islands))
                print("Num of faces:", len(bmCopy.faces))

                islands2D = []
                for f in bmCopy.faces:
                    # First, subtract the vertex position from the planePoint
                    # position so that we get a vector lying in the plane.
                    # Then, apply change-of-basis on this vector to make it 2D
                    # Finally, get just the x and y for this.
                    verts2D = [list(changeOfBasis @ (v.co - planePoint))[:-1] for v in f.verts]
                    islands2D.append(verts2D)

                # We also need to do the same for the original face.
                origFace2D = [list(changeOfBasis @ (v.co - planePoint))[:-1] for v in origFace.verts]

                # b) Calculate the required 2D visual hull.
                scene = Scene()
                print("Creating new scene with polygons:")
                for isle2D in islands2D:
                    scene.addPolygon(isle2D)
                    print(" -", isle2D)
                print("\n\n")
                scene.calcFreeLines()

                # c) Overlap the 2D visual hull with the projected/2D original face.
                vhPolygons = [MyPolygon(f.getCoords()) for f in scene.drawableFaces if (f.visualNumber == 0)]

                scaledClip = []
                for vhPoly in vhPolygons:
                    if not vhPoly.isClockwise():
                        vhPoly.changeOrientation()
                    scaledClip.append(pyclipper.scale_to_clipper(vhPoly.getCoords()))

                subjPolygon = MyPolygon(origFace2D)
                if not subjPolygon.isClockwise():
                    subjPolygon.changeOrientation()
                scaledSubj = pyclipper.scale_to_clipper(subjPolygon.getCoords())

                pc = pyclipper.Pyclipper()
                pc.AddPath(scaledSubj, pyclipper.PT_SUBJECT, True)
                pc.AddPaths(scaledClip, pyclipper.PT_CLIP, True)

                faceIntersectionInts = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
                faceDifferenceInts = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

                faceIntersection = []
                for soln in faceIntersectionInts:
                    scaledSoln = pyclipper.scale_from_clipper(soln)
                    faceIntersection.append(scaledSoln)


                faceDifference = []
                for soln in faceDifferenceInts:
                    scaledSoln = pyclipper.scale_from_clipper(soln)
                    faceDifference.append(scaledSoln)

                # d) "Unproject" the positions
                changeOfBasis.transpose()
                
                intersection3D = []
                for currIntersection in faceIntersection:
                    newIntersection = [list(planePoint + (changeOfBasis @ mathutils.Vector([v[0], v[1], 0.0]))) for v in currIntersection]
                    intersection3D.append(newIntersection)

                difference3D = []
                for currDifference in faceDifference:
                    newDifference = [list(planePoint + (changeOfBasis @ mathutils.Vector([v[0], v[1], 0.0]))) for v in currDifference]
                    difference3D.append(newDifference)
                
                # e) If intersection exists, add it to "discard" mesh.
                discardPolygons += intersection3D
                # f) If difference exists, add it to "keep" mesh.
                keepPolygons += difference3D
            else:
                keepPolygons.append([v.co for v in origFace.verts])

        self._createFaces(keepPolygons, "keepSurface")
        self._createFaces(discardPolygons, "discardSurface")

        return

    def _createFaces(self, polygons, objName):
        new_mesh = bpy.data.meshes.new('new_mesh')

        vertices = []
        edges = []
        faces = []

        # Mesh creation following the tutorial at: https://b3d.interplanety.org/en/how-to-create-mesh-through-the-blender-python-api/
        for polygon in polygons:
            currVertCount = len(vertices)
            vertices += polygon
            polygonFace = tuple(range(currVertCount, currVertCount + len(polygon)))
            faces.append(polygonFace)

        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()

        newObj = bpy.data.objects.new(objName, new_mesh)

        scene = bpy.context.scene
        scene.collection.objects.link(newObj)

    def scenePrintTest(self):
        scene = Scene()
        polygon1 = [(0, 0), (5, 0), (5, 3), (4, 3), (4, 5), (1, 5), (1, 3), (0, 3)]
        polygon2 = [(1, 7), (3, 7), (5, 9), (4, 11), (4, 9), (1, 8), (2, 10), (0, 10)]
        scene.addPolygon(polygon1)
        scene.addPolygon(polygon2)
        scene.calcFreeLines()

        faceCount = 0
        for f in scene.drawableFaces:
            print("Face", faceCount, ":")
            faceCount += 1
            pts = f.getCoords()
            centrePt = np.mean(pts, axis=0)
            print(" - NumPts:", pts.shape[0])
            print(" - VisNum:", f.visualNumber)
            print(" - Pts:")
            for pt in pts:
                print("   -", pt)
        
        return
