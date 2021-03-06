__author__ = 'Rick'

import data
import numpy

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
chips = data.chips

FILL_VALUE = -1
CHIP_VALUE = -2


def createGrid():
    """
    Creates an grid filled with FILL_VALUE
    Only used inner class. For reference to the grid object use grid.grid
    """
    g = numpy.full(shape=(X_SIZE, Y_SIZE, Z_SIZE), fill_value=FILL_VALUE, dtype=type(FILL_VALUE))
    for c in chips:
        g[c[0]][c[1]][c[2]] = CHIP_VALUE
    return g


def isOccupied(point):
    """
    Returns True if the given point or path is occupied
    """
    try:
        point_value = grid[point[0]][point[1]][point[2]]
        if point_value == FILL_VALUE:
            return False
        return True
    except IndexError:
        print "Error occurred in isOccupied"
        print "Point =", point
        return True


def inGrid(point):
    """
    Returns true if point is not in grid
    """
    x, y, z = point[0], point[1], point[2]
    if x < 0 or y < 0 or z < 0 or x >= X_SIZE or y >= Y_SIZE or z >= Z_SIZE:
        return False
    return True


def clearGrid():
    global grid
    grid = createGrid()
    return grid


def rebuildGrid(path_dict):
    """
    Rebuilds grid with the given path_dict
    path_dict = {1: [path], 2:[path], ...}
    """
    global grid
    grid = clearGrid()
    for path_val in path_dict.keys():
        for point in path_dict[path_val][1:-1]:
            grid[point[0]][point[1]][point[2]] = path_val

def minPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1]) + abs(points[0][2] - points[1][2])


def notInGrid(point):
    """
    Returns true if point is not in grid
    """
    x, y, z = point[0], point[1], point[2]
    if x < 0 or y < 0 or z < 0 or x >= X_SIZE or y >= Y_SIZE or z >= Z_SIZE:
        return True
    return False


def getOccupation(path):
    """
    Returns a list of indexes of lines the path intersects
    """
    intersections = []
    for point in path[1:-1]:
        point_value = grid[point[0]][point[1]][point[2]]
        if point_value != FILL_VALUE and point_value not in intersections:
            intersections.append(point_value)
    intersections = set(intersections)
    try:
        intersections.remove(-2)
    except KeyError:
        pass
    intersections = list(intersections)
    return intersections


def getPointOccupation(point):
    """
    Returns the value of the point in the grid
    """
    return grid[point[0]][point[1]][point[2]]


def setOccupation(path, grid_value):
    """
    Sets points in the grid as occupied. The number in the grid corresponds to the drawn line number.
    """
    for point in path[1:-1]:
        grid[point[0]][point[1]][point[2]] = grid_value


def setPointOccupation(point, grid_value):
    grid[point[0]][point[1]][point[2]] = grid_value


def clearOccupation(path):
    """
    Clears the path from the grid. It sets the 'empty value' to all points of the given path
    """
    for point in path[1:-1]:
        grid[point[0]][point[1]][point[2]] = FILL_VALUE

grid = createGrid()  # Create the variable grid for usage from other files. Reference to this variable.