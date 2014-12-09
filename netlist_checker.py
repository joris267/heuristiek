import itertools
import numpy as np
import data as data
import random
import copy

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
chips = data.chips
netlist = data.netlist


def findFreeNeighbours(point):
    neighbours = []
    for dimension in range(3):
        for direction in range(-1, 2, 2):
            if point[2] == 7:
                if direction == 1 and dimension == 3:
                    continue
            list_point = list(point)

            list_point[dimension] += direction
            neighbour = tuple(list_point)
            if inGrid(neighbour) and isFree(neighbour):
                neighbours.append(neighbour)
    return neighbours


def inGrid(point):
    return (0 <= point[0] < X_SIZE) and (0 <= point[1] < Y_SIZE) and (0 <= point[2] < Z_SIZE)


def connectionsPerChip(netlist, chips = None):
    """
    returns a dictionary with the chip as key and the number of connections as value
    """

    chip_to_occurrences = {}

    # list(itertools.chain.from_iterable(netlist)) is quickest way to chain items in a list together in a new list
    chips_in_netlist = list(itertools.chain.from_iterable(netlist))
    if chips != None:  # needed for algortime J find neighbours in neighbourgrid
        chips_in_netlist += range(len(chips))

    # bincount counts occurrences of integers in list. Value is put at the index
    # i.e. np.bincount([0,1,1,4]) => [0,2,0,0,1]
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.bincount.html
    occurrences = np.bincount(chips_in_netlist)
    for i in range(len(occurrences)):
        chip_to_occurrences[i] = occurrences[i]
    if chips != None:
        for i in range(len(chip_to_occurrences)):
            chip_to_occurrences[i] -= 1
    return chip_to_occurrences


def isFree(point):
    """
    For a given point (x,y,z) returns True if Free, else False
    """
    global grid
    for i in point:
        if i < 0:
            return False
    try:
        value = grid[point[0]][point[1]][point[2]]
    # print value
    except:
        # print "point ", point, "lies outside of grid"
        return False
    return value == -1


def checkDouble(netlist):
    doubles = []
    for net1 in netlist:
        reversed_net = (net1[1], net1[0])
        occurces = 0
        for net2 in netlist:
            if net1 == net2 or net2 == reversed_net:
                occurces += 1


        for _ in range(occurces - 1):
            doubles.append(net1)

    print "removing doubles: ", doubles
    for double in doubles:
        try:
            netlist.remove(double)
        except:
            netlist.remove((double[1], double[0]))

    return netlist


def checkBeginIsEnd(netlist):
    start_is_end = []
    for net in netlist:
        if net[0] == net[1]:
            start_is_end.append(net)

    print "removing ", start_is_end
    for net in start_is_end:
        netlist.remove(net)

    return netlist

def checkConenctions(netlist):
    connections_dict = connectionsPerChip(netlist)
    chips_in_netlist = set(list(itertools.chain.from_iterable(netlist)))
    for chip in chips_in_netlist:
        if connections_dict[chip] > 5:
            print chip, "has %s connections and some will have to be removed" %(str(connections_dict[chip]))


def createGrid():
    """
    creates an grid filled with True except on the points in chips
    imports chips, X_SIZE, Y_SIZE and Z_SIZE from data
    """
    grid = np.ones(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=int)
    grid.fill(-1)
    for chip in chips:
        grid[chip[0]][chip[1]][chip[2]] = -2
    return grid


def setValue(point, value = False):
    if inGrid(point):
        grid[point[0]][point[1]][point[2]] = value


def checkConnectionPerChp(netlist):
    """
    checks if chips have to manny connections
    returns a list of chips that have to manny connections
    """
    connections_dict = connectionsPerChip(netlist)
    chips_in_netlist = set(list(itertools.chain.from_iterable(netlist)))
    for chip, chip_index in zip(chips_in_netlist, range(len(chips_in_netlist))):
        connections = connections_dict[chip]
        free_neighbours = findFreeNeighbours(chips[chip])
        for _ in range(connections):
            if len(free_neighbours) == 0:
                break
            first_step = random.choice(free_neighbours)
            setValue(first_step, chip_index)
            free_neighbours.remove(first_step)
            connections_dict[chip] -= 1

    unlayable_paths = [(chip, connections_dict[chip]) for chip in connections_dict if connections_dict[chip] > 0]
    print "chips that have unlayable connetions", unlayable_paths
    return unlayable_paths




def checkMacConnectionDensity(chips):
    max_connections = 0

    for chip_index in range(len(chips)):
        free_neighbours = findFreeNeighbours(chips[chip_index])
        max_connections += len(free_neighbours)
        connections = len(free_neighbours)
        for _ in range(connections):
            if len(free_neighbours) == 0:
                break
            first_step = random.choice(free_neighbours)
            setValue(first_step, chip_index)
            free_neighbours.remove(first_step)
    return max_connections

def checkMacConnectionDensityPerChips(chips):
    max_connections = {}

    for chip_index in range(len(chips)):
        free_neighbours = findFreeNeighbours(chips[chip_index])
        connections = len(free_neighbours)
        max_connections[chip_index] = connections
        for _ in range(connections):
            first_step = random.choice(free_neighbours)
            setValue(first_step, chip_index)
            free_neighbours.remove(first_step)
    return max_connections


def remove_overloads(netlist):
    connections_overload = checkConnectionPerChp(netlist)
    netlist_temp = copy.deepcopy(netlist)
    nets_to_remove = []
    for chip, overload in connections_overload :
        nets_to_remove = []
        for net in nets_to_remove:
            netlist_temp.remove(net)
        for _ in range(overload):
            for net in netlist_temp:
                if chip in net:
                    nets_to_remove.append(net)
                    break
    for net in nets_to_remove:
        netlist_temp.remove(net)
    netlist = netlist_temp
    return  netlist


def findValidNets(N, netlist):
    valid_nets = []
    open_chips = checkMacConnectionDensityPerChips(chips)
    full_chips = []

    #removing empty chips
    for chip in open_chips:
        if open_chips[chip] == 0:
           full_chips.append(chip)

    for chip in full_chips:
        del open_chips[chip]


    for i in range(N):
        start = random.choice(open_chips.keys())
        for i in range(100):  # max tries to find a open path
            end = random.choice(open_chips.keys())
            if end != start and (start,end) not in valid_nets and (start,end) not in netlist \
                    and (end, start) not in valid_nets and (end, start) not in netlist:
                break

        open_chips[start] -= 1
        if open_chips[start] == 0:
            del open_chips[start]
        open_chips[end] -= 1
        if open_chips[end] == 0:
            del open_chips[end]

        valid_nets.append((start,end))

    return valid_nets

if __name__ == "__main__":
    print len(data.netlist_1)
    print len(data.netlist_2)
    print len(data.netlist_3)
    print len(data.netlist_4)
    print len(data.netlist_5)
    print len(data.netlist_6)
    number_of_nets = 50
    grid = createGrid()
    netlist = data.netlist
    print "maximum number of connections = %i"%(checkMacConnectionDensity(chips)/2)
    grid = createGrid()  # need a resst since checkMacConnectionDensity() changes occupation
    netlist = checkBeginIsEnd(netlist)
    netlist = checkDouble(netlist)
    netlist = remove_overloads(netlist)


    #remove if netlist to long
    if len(netlist) > number_of_nets:
        nets_to_remove = []
        for _ in range(len(netlist) - number_of_nets):
            nets_to_remove.append(random.choice(netlist))
        for net in nets_to_remove:
            netlist.remove(net)

    #add if netllist to short
    while len(netlist) < number_of_nets:
        new_nets = findValidNets(number_of_nets - len(netlist), netlist)
        netlist += new_nets





    print "current netlist length: ", len(netlist)
    print connectionsPerChip(netlist)
    print netlist


