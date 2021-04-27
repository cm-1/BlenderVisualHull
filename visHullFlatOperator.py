import bpy
import bmesh

import numpy as np
import math

from .visHullTwoD import Scene

class FlatVisHullCreator:
    def __init__(self):
        print("Creating FlatVisHullCreator")

    def getPoints(self):
        # Get the active mesh
        obj = bpy.context.object


        scene = Scene()

        polyCount = 0
        for poly in obj.data.polygons:
            polyVerts = []
            for vi in poly.vertices:
                newVert = (obj.data.vertices[vi].co.x, obj.data.vertices[vi].co.y)
                polyVerts.append(newVert)
            print("polygon{0} = {1}".format(polyCount, polyVerts))
            scene.addPolygon(polyVerts)
            polyCount += 1
        scene.calcFreeLines()


        vertices = []
        edges = []
        faces = []

        print("Drawable faces:")
        for f in scene.drawableFaces:
            print(" - VN: {0}, Verts: {1}".format(f.visualNumber, f.getCoords()))
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