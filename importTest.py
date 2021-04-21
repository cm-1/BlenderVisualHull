import numpy as np
import math

from .nestedImportTest import PointPrinter

class PointCreator:
    def __init__(self, varToUse):
        self.varToUse = varToUse

    def getPoints(self, start, end, numPoints):

        xVals = np.linspace(start, end, numPoints)

        testFunc = lambda a: (10.0*np.sin(a) - self.varToUse)

        yVals = testFunc(xVals)

        retVal = np.column_stack((xVals, yVals))

        print("\nTest message here!\n")

        printer = PointPrinter(retVal)
        printer.printPoints()

        return retVal
