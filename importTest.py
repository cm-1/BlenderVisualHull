import numpy as np
import math

from .visHullTwoD import Scene

class PointCreator:
    def __init__(self, varToUse):
        self.varToUse = varToUse

        

    def getPoints(self, start, end, numPoints):

        xVals = np.linspace(start, end, numPoints)

        testFunc = lambda a: (10.0*np.sin(a) - self.varToUse)

        yVals = testFunc(xVals)

        retVal = np.column_stack((xVals, yVals))

        print("\nTest message here!\n")

        self.scenePrintTest()

        return retVal

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
