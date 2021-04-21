class PointPrinter:
    def __init__(self, points):
        self.points = points

    def printPoints(self):

        print("Points:")
        for p in self.points:
            print(" -", p)

        return