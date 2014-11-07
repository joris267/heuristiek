import numpy as np
import data as data
import operator
import itertools
import random

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
chips = data.chips
netlist = data.netlist


def createGrid():
    """
    creates an grid filled with True except on the points in chips
    will assume chips are on layer 3 unless other int is given
    imports chips, X_SIZE, Y_SIZE and Z_SIZE from visualization
    """
    grid = np.ones(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=bool)
    for chip in chips:
        grid[chip[0]][chip[1]][0] = False
    return grid


def isOccupied(point):
    """
    For a given point (x,y,z) returns True if occupied, else False
    """
    return grid[point[0]][point[1]][point[2]]

def setOccupation(point, occupation):
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


def findShortestPath(start, end):
    """
    Algorithm that finds shortest intersecting path between 2 points
    Returns a list of points that make up the shortest path in one layer
    """
    z = start[2]
    x_start = min([start[0], end[0]])
    if x_start == start[0]:
        x_end = end[0]
        y_start = start[1]
        y_end = end[1]
    else:
        x_end = start[0]
        y_start = end[1]
        y_end = start[1]

    path_points = []
    conflicts = []

    for i in range(x_end - x_start + 1):
        if isOccupied((i, y_start, z)):
            conflicts.append(i)
        path_points.append((x_start + i, y_start, start[2]))

    if y_end != y_start:
        direction = (y_end - y_start) / abs(y_end - y_start)  # -1 or 1
        for j in range(0, y_end - y_start + direction, direction):
            if isOccupied((x_end, j, z)):
                conflicts.append(j)
            path_points.append((x_end, y_start + j, end[2]))

    print len(conflicts)
    return path_points


def calculateWireLenght(path_list):
    """
    Calculates the total length of all the paths
    input is a list of lists in the form:
    [[(start_path_1), (point_path_1), (end_path_1)], [path_2...]]
    """

    total_length = 0
    for path in path_list:
        total_length += len(path)
    return total_length


def checkIntsections(path_list):
    """
    Checks if there are intersections in the path.
    Returns the number of intersections in the path
    """
    joined_list = list(itertools.chain.from_iterable(path_list))
    unique_points = len(set(joined_list))
    total_points = len(joined_list)
    return total_points - unique_points


def connectionsPerChip(netlist):
    """
    returns a dictionary with the chip as key and the number of connections as value
    """

    chip_to_occurrences = {}

    # list(itertools.chain.from_iterable(netlist)) is quickest way to chain items in a list together in a new list
    chips_in_netlist = list(itertools.chain.from_iterable(netlist))

    # bincount counts occurrences of integers in list. Value is put at the index
    # i.e. np.bincount([0,1,1,4]) => [0,2,0,0,1]
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.bincount.html
    occurrences = np.bincount(chips_in_netlist)
    for i in range(len(occurrences)):
        chip_to_occurrences[i] = occurrences[i]
    return chip_to_occurrences


def doubleStartEndPoints(netlist, chip_to_occurrences = None):
    """
    Find the number of double start/end points, that is, the sum of al occurrences higher then 1.

    """
    som = 0
    if chip_to_occurrences == None:
        chips_in_netlist = list(itertools.chain.from_iterable(netlist))
        occurrences = np.bincount(chips_in_netlist)
        for i in occurrences:
            if i > 1:
                som += i

    else:
        for i in chip_to_occurrences.values():
            if i > 1:
                som += 1

    return som

def endpointsChips(netlist):
    """
    returns dictonary of the connections a chip has:
    i.e. {1:[1,2], 2:[3,23]}
    """
    chip_to_chips = {}
    for chip in range(len(chips)):
        temp_list = []
        for connection in netlist:
            if chip in connection:
                temp_list.append(connection)
        if len(temp_list) == 0:
            print "chip %i has no connections"%(chip)
        else:
            temp_list = set(itertools.chain.from_iterable(temp_list))
            temp_list.remove(chip)
            chip_to_chips[chip] = temp_list

    return chip_to_chips

def theoreticalShortestPaths(netlist):
    """
    Find the theoretical shortest paths
    returns a list of lists with the path points
    """
    global chips
    shortest_paths = []
    for i in range(len(netlist)):
        start = chips[netlist[i][0]]
        end = chips[netlist[i][1]]
        shortest_paths.append(findShortestPath(start, end))

    return shortest_paths

def calculateEndStart(start, end):
    z = start[2]
    x_start = min([start[0], end[0]])
    if x_start == start[0]:
        x_end = end[0]
        y_start = start[1]
        y_end = end[1]
    else:
        x_end = start[0]
        y_start = end[1]
        y_end = start[1]

    return x_start, x_end, y_start, y_end

def findPossiblePathSameLayer(start, end):
    x_start, x_end, y_start, y_end = calculateEndStart(start, end)
    path_points = []

    if random.randrange(2): # start x direction
        for i in range(x_end - x_start + 1):
            if not isOccupied((i, y_start, z)):
                path_points.append((x_start + i, y_start, start[2]))

            else:



    if y_end != y_start:
        direction = (y_end - y_start) / abs(y_end - y_start)  # -1 or 1
        for j in range(0, y_end - y_start + direction, direction):
            if isOccupied((x_end, j, z)):
                conflicts.append(j)
            path_points.append((x_end, y_start + j, end[2]))

    print len(conflicts)
    return path_points


if __name__ == "__main__":
    grid = createGrid()
    print connectionsPerChip(data.netlist)
    print endpointsChips(data.netlist)

    # sortDistance(netlist)
    # findShortestPath((1,1,3),(9,4,3))
