__author__ = 'Rick'

import data
import numpy

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE

FILL_VALUE = -1


def createGrid():
    """
    Creates an grid filled with 0's
    """
    return numpy.full(shape=(X_SIZE, Y_SIZE, Z_SIZE), fill_value=FILL_VALUE, dtype=int)


def isOccupied(input):
    """
    Returns True if the given point or path is occupied
    """
    if type(input[0]) == int:  # Input is a point
        point = input
        if grid[point[0]][point[1]][point[2]] == FILL_VALUE:
            return False
        return True
    if type(input[0]) == tuple or type(input[0] == list):  # Input is a tuple or a list
        path = input
        for point in path:
            if grid[point[0]][point[1]][point[2]] == FILL_VALUE:
                continue
            else:
                return True
        return False


def setOccupation(path, index):
    for index, point in enumerate(path):
        if index != 0 or index != len(path):
            grid[point[0]][point[1]][point[2]] = index


def clearOccupation(path):
    for point in path:
        grid[point[0]][point[1]][point[2]] = 0

grid = createGrid()