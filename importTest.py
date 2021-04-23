import bpy
import bmesh

import numpy as np
import math

from .visHullTwoD import Scene

class PointCreator:
    def __init__(self):
        print("Creating PointCreator")

    def getPoints(self):
        # Get the active mesh
        obj = bpy.context.object


        scene = Scene()

        for poly in obj.data.polygons:
            polyVerts = []
            for vi in poly.vertices:
                newVert = (obj.data.vertices[vi].co.x, obj.data.vertices[vi].co.y)
                polyVerts.append(newVert)
            scene.addPolygon(polyVerts)
        scene.calcFreeLines()


        vertices = []
        edges = []
        faces = []

        for f in scene.drawableFaces:
            if f.visualNumber == 0:
                currVertCount = len(vertices)
                pts = f.getCoords()
                vertices += [(v[0], v[1], 0) for v in pts]
                polygonFace = tuple(range(currVertCount, currVertCount + len(pts)))
                faces.append(polygonFace)


        new_mesh = bpy.data.meshes.new('new_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()


        # Mesh replacement/removal learned from an answer by user satishgoda 
        # on Blender StackExchange submitted 2019-08-10 in response to the
        # question "Is there any way to replace an object?" asked by user atek
        # on 2016-10-16. Link to the answer:
        # https://blender.stackexchange.com/a/148084
        # The question has also been web archived at:
        # http://web.archive.org/web/20201112022110/https://blender.stackexchange.com/questions/65128/is-there-any-way-to-replace-an-object
        meshToRemove = obj.data

        obj.data = new_mesh

        if meshToRemove.users or meshToRemove.use_fake_user:
            print("Guess I don't remove it.")
        else:
            bpy.data.meshes.remove(meshToRemove)

        return

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
