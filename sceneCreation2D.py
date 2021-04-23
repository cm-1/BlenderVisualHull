import bpy
import numpy as np

class SceneCreator2D:
    def __init__(self, sceneNum):
        self.sceneNum = sceneNum
        scene0 = {}
        scene0[0] = [(0, 0), (2.25, 0.5), (1.25, 2.3)] # [(0,3),(1,1),(3,0),(4,0),(3,4)]
        scene0[1] = [(1.15, 3.15), (4, 4), (0.9, 5.25)] # [(1,4),(2,5),(2,1),(1,3)]
        scene0[2] = [(3, 0.7), (4.85, 1.75), (4.85, 3.4)]

        scene1 = {}

        scene1[0] = [(0, 0), (5, 0), (5, 5), (4, 5), (4, 3), (1, 3), (1, 5), (0, 5)]

        scene2 = {}
        scene2[0] = [(0, 0), (5, 0), (5, 3), (4, 3), (4, 5), (1, 5), (1, 3), (0, 3)]
        scene2[1] = [(1, 7), (3, 7), (5, 9), (4, 11), (4, 9), (1, 8), (2, 10), (0, 10)]

        scene3 = {}
        polygon1 = [(0, 2), (1,1), (2,2), (1,0)]
        polygon2 = [(3,3), (4,2), (5,3)]
        # polygon2 = [(p[0] - 3, p[1]) for p in polygon2]
        # Horizontal flip for testing purposes.
        # polygon1 = [(-p[0], p[1]) for p in polygon1]
        # polygon2 = [(-p[0], p[1]) for p in polygon2]
        scene3[0] = polygon1
        scene3[1] = polygon2

        scene4 = {}
        scene4[0] = [(0, 7), (2.25, 5), (1.25, 4), (5, 5)] # [(0, 0), (2.25, 0.5), (1.25, 2.3)] # [(0,3),(1,1),(3,0),(4,0),(3,4)]
        scene4[1] = [(1.15, -3.15), (4, -4), (2, -7), (0.9, -5.25)] #[(1.15, 3.15), (4, 4), (0.9, 5.25)] # [(1,4),(2,5),(2,1),(1,3)]
        scene4[2] = [(3, 1), (3, 0.0), (4.85, 0.75), (4.85, 2.4), (5,4)] #[(3, 0.7), (4.85, 1.75), (4.85, 3.4)]
        scene4[3] = [(-0.5, -1), (-0.5, 1.0), (0.5, 1), (0.5, -1)] #[(3, 0.7), (4.85, 1.75), (4.85, 3.4)]

        scene5 = {}
        scene5[0] = [(0, 0.6), (1.5, 0), (2.5, 1.25), (1.25, 0.75), (1.125, 1.8)]
        scene5[1] = [(1.3, 2.25), (2.8, 2.8), (1.65, 3.125)]
        scene5[2] = [(2.8, 1.25), (4.125, 0.25), (3.5, 2.0)]

        scene6 = {}
        scene6[0] = [(0,0), (2.5, 0), (0, 1.5)]
        scene6[1] = [(0, 3.25), (5, 4.25), (0, 4.25)]
        scene6[2] = [(3.5, 0), (5, 0), (5, 2.75), (3.5, 2.75)]

        self.scenes = [scene0, scene1, scene2, scene3, scene4, scene5, scene6]

    def createScene(self):
        sceneInfo2D = self.scenes[self.sceneNum]

        new_mesh = bpy.data.meshes.new('new_mesh')

        vertices = []
        edges = []
        faces = []

        # Mesh creation following the tutorial at: https://b3d.interplanety.org/en/how-to-create-mesh-through-the-blender-python-api/
        for polygon in sceneInfo2D.values():
            currVertCount = len(vertices)
            vertices += [(v[0], v[1], 0) for v in polygon]
            polygonFace = tuple(range(currVertCount, currVertCount + len(polygon)))
            faces.append(polygonFace)
            

        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()

        scene2D = bpy.data.objects.new('scene2D', new_mesh)

        scene = bpy.context.scene
        scene.collection.objects.link(scene2D)
        #scene2D.select = True

        '''
        collectionToUpdate = None
        print("Type of collections:", type(bpy.data.collections))
        if len(bpy.data.collections) > 0:
            collectionToUpdate = bpy.data.collections[0]
        else:
            collectionToUpdate = bpy.data.collections.new('scene_2D_collection')
            bpy.context.scene.collection.children.link(collectionToUpdate)
        collectionToUpdate = objects.link(scene2D)
        '''

