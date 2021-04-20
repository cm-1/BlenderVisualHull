import numpy as np
import math

class PointCreator:
    def __init__(self, varToUse):
        self.varToUse = varToUse

    def getPoints(self, start, end, numPoints):

        xVals = np.linspace(start, end, numPoints)

        testFunc = lambda a: (10.0*np.arctan(a) - self.varToUse)

        yVals = testFunc(xVals)

        retVal = np.column_stack((xVals, yVals))

        return retVal
