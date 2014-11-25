from algoritme_j import *
import data
import os, os.path
import itertools
import numpy as np

netlist = data.netlist

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
        if isFree((i, y_start, z)):
            conflicts.append(i)
        path_points.append((x_start + i, y_start, start[2]))

    if y_end != y_start:
        direction = (y_end - y_start) / abs(y_end - y_start)  # -1 or 1
        for j in range(0, y_end - y_start + direction, direction):
            if isFree((x_end, y_start + j, z)):
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
        if len(path)> 1:
            total_length += len(path) - 1  # path bestaand uit N punten heet N - 1 ridges
    return total_length


def checkIntsections(path_list):
    """
    Checks if there are intersections in the path.
    Returns the number of intersections in the path
    """
    joined_list = list(itertools.chain.from_iterable(path_list))
    unique_points = set(joined_list)
    doubles = 0

    for unique_point in unique_points:
        count = 0
        for point in joined_list:
            if unique_point == point:
                count += 1
        if count > 1:
            doubles += count

    return doubles


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


def doubleConnections(netlist):
    doubles = []
    for net in netlist:
        occurces = 0
        reversed_net = (net[1], net[0])
        for net2 in netlist:
            if net == net2 or reversed_net == net2:
                occurces += 1
        if occurces > 1:
            doubles.append(net)
    return doubles


def getAvrgValueAStarDistance(grid):
    total = 0
    points = 0
    for i in grid:
        for j in i:
            for k in j:
                points += 1
                total += k[0]  # k is the value containing [distance, [intersections]]
    return total / float(points)




def doubleStartEndPoints(netlist, chip_to_occurrences=None):
    """
    Find the number of double start/end points, that is, the sum of al occurrences higher then 1.
    """
    som = 0
    if chip_to_occurrences is None:
        chips_in_netlist = list(itertools.chain.from_iterable(netlist))
        occurrences = np.bincount(chips_in_netlist)
        print netlist, chips_in_netlist
        print occurrences
        for i in occurrences:
            if i > 1:
                som += i

    else:
        for i in chip_to_occurrences.values():
            if i > 1:
                som += i

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


def areNeighbours(point1, point2):
    distance = 0
    for dimension in range(3):
        distance += (point1[dimension] - point2[dimension])**2
    distance = distance**.5
    return distance == 1


def smoothenPath(path):
    for  i in range(len(path)):
        for j  in range(i+2, len(path)):
            if areNeighbours(path[i], path[j]):
                return smoothenPath(path[:i+1] + path[j:])  # plus 1 to include endpoint
    return path



def create_folder(container, name):

    try:
        os.listdir(container)
    except:
        os.makedirs(container)

    # version = 0


    try:
        os.listdir(container + "\\" + name)
    except:
        os.makedirs(container + "\\" + name)

    folder_name = container + "\\\\" + name
    return folder_name
        # while True:
        #     try:
        #         folder_name = container + "\\" + name + " (%i)"%(version)
        #         os.makedirs(folder_name)
        #         return folder_name
        #     except:
        #         version += 1

def write_file(folder_path, file_name, stuf):
    total_file_dir = folder_path + "\\\\" + file_name

    total_file_path = total_file_dir + ".txt"
    if os.path.exists(total_file_path):  # if succeeds the file exists
        copy = 0
        while True:
            copy += 1
            total_file_path = total_file_dir + " (%i)"%(copy)  + ".txt"
            if not os.path.exists(total_file_path):
                break


    bestand  = open(total_file_path, "w+")
    for i in stuf:
        bestand.write(str(i))
    bestand.close()


def safe(netlist, shortest_paths, relay_list):
    aantal_paden_gelegd = len([path for path in shortest_paths.values() if len(path) > 0])
    totaal_paden = len(netlist)
    datum = time.strftime("%d-%m-%Y")
    folder_name = create_folder("oplossingen Joris", datum)
    lengte_oplossing = calculateWireLenght(shortest_paths.values())
    file_name = str(lengte_oplossing) + " " + str(aantal_paden_gelegd) + " vd " + str(totaal_paden)
    write_file(folder_name, file_name, [relay_list] + [shortest_paths])

if __name__ == "__main__":
    #example where line becomes a lot shorter by smoothening it
    path = [(4, 1, 3), (4, 1, 4), (4, 1, 3), (4, 0, 3), (3, 0, 3), (3, 1, 3), (3, 2, 3), (2, 2, 3), (2, 1, 3),
            (1, 1, 3), (1, 2, 3), (1, 2, 4), (1, 1, 4), (2, 1, 4), (3, 1, 4), (3, 1, 5), (4, 1, 5), (5, 1, 5),
            (5, 1, 4), (5, 1, 3), (5, 2, 3), (5, 3, 3), (5, 3, 4), (4, 3, 4), (4, 2, 4), (3, 2, 4), (3, 3, 4),
            (3, 3, 3), (2, 3, 3), (1, 3, 3), (1, 4, 3)]

    # path_list = [path, smoothenPath(path)]
    # print "length", len(path_list[0])
    # print "smoothed length", len(path_list[1])
    # print path_list
    print connectionsPerChip(netlist)
    print len(netlist)
   #  Visualization.runVisualization(path_list)
