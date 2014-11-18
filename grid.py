import numpy as np
import data as data
import operator
import itertools
import random
import algoritme_j as algoritme

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
chips = data.chips
netlist = data.netlist


def createGrid():
    """
    creates an grid filled with True except on the points in chips
    imports chips, X_SIZE, Y_SIZE and Z_SIZE from data
    """
    grid = np.ones(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=bool)
    for chip in chips:
        grid[chip[0]][chip[1]][chip[2]] = False
    return grid


def createPathGrid():
    """
    Creates a grid filled with -1 to keep track of which paths are where.
    imports chips, X_SIZE, Y_SIZE and Z_SIZE from data
    """
    path_grid = np.ndarray(shape=(X_SIZE+1, Y_SIZE+1, Z_SIZE+1), dtype=int)
    path_grid.fill(-1)
    return path_grid

def isOccupied(point):
    """
    For a given point (x,y,z) returns True if occupied, else False
    """
    return grid[point[0]][point[1]][point[2]]


def setOccupation(point, occupation=False):
    """
    For a given point changes it's value in the grid to the given occupation.
    Returns nothing.
    """
    grid[point[0]][point[1]][point[2]] = occupation


def sortDistance(netlist):
    """
    For a given netlist calculates the distances between the given to be connected chips. Then returns
    the netlist sorted by distance (shortest distance first).
    """
    netlist_dictionary = {}
    for i in range(len(netlist)):
        start = chips[netlist[i][0]]
        end = chips[netlist[i][1]]

        delta_x = abs(start[0]-end[0])
        delta_y = abs(start[1]-end[1])
        distance = delta_x + delta_y

        netlist_dictionary[(netlist[i][0], netlist[i][1])] = distance

    sorted_dictionary = sorted(netlist_dictionary.items(), key=operator.itemgetter(1))
    sorted_netlist = []
    for j in range(len(sorted_dictionary)):
        sorted_netlist.append(sorted_dictionary[j][0])

    return sorted_netlist

grid = createGrid()

if __name__ == "__main__":
    print algoritme.connectionsPerChip(data.netlist)
    print algoritme.endpointsChips(data.netlist)

    # sortDistance(netlist)
    # findShortestPath((1,1,3),(9,4,3))
