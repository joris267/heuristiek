import copy
import path_saver
import random
import time
import data
import grid_copy as grid
from heapq import *
import Visualization

seed = 34  # 34 is best so far
random.seed(str(seed))
chips = data.chips
netlist = data.netlist
print "Netlist size:", len(netlist)

data_grid = grid.grid

nets_unsorted = []          # List with start and end points of lines
index_path_dict = {}        # Dictionary with net-index as key and the path as value
conn_per_chip = {}          # Dictionary with the number of
conn_free_per_chip = {}
not_used_chips = []
not_layed_paths = []
path_lay_amount = {}
visualise_dict = {}


def initialise():
    for k, path in enumerate(netlist):  # Making routes_unsorted
        path_lay_amount[k] = 1
        visualise_dict[k] = []
        chip_start = path[0]
        chip_end = path[1]
        nets_unsorted.append((chips[chip_start], chips[chip_end]))
        if chips[chip_start] not in conn_per_chip:  # Check connections per chip
            conn_per_chip[chips[chip_start]] = 1
        else:
            conn_per_chip[chips[chip_start]] += 1
        if chips[chip_end] not in conn_per_chip:
            conn_per_chip[chips[chip_end]] = 1
        else:
            conn_per_chip[chips[chip_end]] += 1

    if len(conn_per_chip.keys()) != len(chips):  # Check if there are chips that aren't used
        print "Number of chips used:", len(conn_per_chip.keys())
        print "Number of chips on board:", len(chips)
        print "Some chips are useless!"
        for chip in chips:
            if chip not in conn_per_chip.keys():
                not_used_chips.append(chip)
        for chip in not_used_chips:
            chips.remove(chip)
        print "Not used chips:", not_used_chips
        print "Delete chip from chiplist..."
        if len(conn_per_chip.keys()) != len(chips):
            raise StandardError


def findNeighbours(point):
    """
    Returns all the neighbours from the given point
    """
    neighbours = []
    for dimension in range(3):
        for direction in range(-1, 2, 2):
            if point[2] == 7:
                if direction == 1 and dimension == 3:
                    continue
            list_point = list(point)

            list_point[dimension] += direction
            neighbour = tuple(list_point)
            if grid.inGrid(neighbour):
                neighbours.append(neighbour)
    return neighbours


def getChipsNeighbours(points):
    """
    Returns all the points next to all chips (except at the given points)
    """
    chips_copy = copy.deepcopy(chips)
    for point in points:
        chips_copy.remove(point)
    all_neighbours = []
    for chip in chips_copy:
        all_neighbours += findNeighbours(chip)

    all_neighbours = list(set(all_neighbours))  # Remove doubles in list
    for point in points:  # Clear points next to given points
        for neighbour in findNeighbours(point):
            if neighbour in all_neighbours:
                all_neighbours.remove(neighbour)

    return all_neighbours


def getNeighbourChips(point):
    """
    Returns all the chips next to the given point
    """
    neighbour_chips = []
    for neighbour in findNeighbours(point):
        if neighbour in chips:
            neighbour_chips.append(neighbour)
    return neighbour_chips


def minPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1]) + abs(points[0][2] - points[1][2])


def aStar(point1, point2, line_val, mode="no_intersections"):
    global conn_free_per_chip
    queue = []  # (f, g, h, point, path_to_point, conn_free_per_chip), point = (x, y, z)
    g = 0
    h = minPathLength((point1, point2))
    f = g + h
    visited_points = []
    heappush(queue, (f, g, h, point1, [point1], conn_free_per_chip))
    chips_neighbours = getChipsNeighbours((point1, point2))

    while queue != []:
        q = heappop(queue)
        conn_free_copy = q[5]
        for successor in findNeighbours(q[3]):
            if successor in visited_points:
                continue
            visited_points.append(successor)
            # if successor in chips_neighbours:
            #     continue
            if successor == point2:
                conn_free_per_chip = q[5]
                return q[4] + [successor]
            g = q[1] + 1
            h = minPathLength((successor, point2))
            f = g + h
            if mode == "with_intersections" and grid.isOccupied(successor):
                if grid.getPointOccupation(successor) != -2:
                    g += 50 * path_lay_amount[grid.getPointOccupation(successor)]
                    f = g + h
            if mode == "no_intersections" and grid.isOccupied(successor):
                continue
            if successor in chips_neighbours:                # Paths are allowed to have a path next to a chip
                valid = True                                 # which isn't the start or end points
                for chip in getNeighbourChips(successor):    # BUT: only when there are unused spots available for that
                    if conn_free_per_chip[chip] <= 0:        # particular chip; chips don't always use their maximum
                        valid = False                        # available free spots
                        break                                #
                    else:                                    #
                        conn_free_copy = copy.deepcopy(conn_free_per_chip)
                        conn_free_copy[chip] -= 1            #
                        g += 50                              # Avoid laying a line next to a chip, but it is possible
                        f = g + h                            # Therefore a penalty of 50 is given
                if not valid:                                #
                    continue                                 #
            item = (f, g, h, successor, q[4] + [successor], conn_free_copy)
            heappush(queue, item)

    print "Path not found for:", line_val, "Points:", point1, point2
    not_layed_paths.append((line_val, (point1, point2)))
    return []


def main():
    initialise()
    img_no = 0
    for chip in conn_per_chip.keys():
        free = len(findNeighbours(chip)) - conn_per_chip[chip]
        conn_free_per_chip[chip] = free

    netlist_sorted = sorted(nets_unsorted, key=minPathLength)  # Sort nets_unsorted by minimum length

    for index, net in enumerate(netlist_sorted):
        path = aStar(net[0], net[1], index)
        if path != []:
            index_path_dict[index] = path
            visualise_dict[index] = path
            #Visualization.run3DVisualisation(visualise_dict.values(), img_no)  # For making a movie
            img_no += 1
            grid.setOccupation(path, index)

    print "No of paths layed:", len(netlist) - len(not_layed_paths)
    print "\n### Starting A* with intersections ###"
    max_iteration = 500
    iteration = 0
    while not_layed_paths != []:
        iteration += 1
        if iteration == max_iteration:
            return []
        print "Iteration", iteration
        print "Paths layed:", len(netlist) - len(not_layed_paths)
        index, net = random.choice(not_layed_paths)
        print "Path " + str(index) + ":", net
        path = aStar(net[0], net[1], index, mode="with_intersections")
        visualise_dict[index] = path
        intersections = grid.getOccupation(path)
        print "Intersecting paths", intersections
        for intersection in intersections:
            path_lay_amount[intersection] += 1
            visualise_dict[intersection] = []
            grid.clearOccupation(index_path_dict[intersection])
            del index_path_dict[intersection]
            not_layed_paths.append((intersection, netlist_sorted[intersection]))

        not_layed_paths.remove((index, net))
        grid.setOccupation(path, index)
        index_path_dict[index] = path
        #Visualization.run3DVisualisation(visualise_dict.values(), img_no)  # For making a movie
        img_no += 1

    return index_path_dict.values()


def runMain():
    start = time.clock()
    paths = main()
    print "Calculated in:", time.clock() - start
    if paths == []:
        print "Could not finish in given number of iterations"
    else:
        print "Amount of paths", len(paths)
        total_length = 0
        for path in paths:
            total_length += len(path) - 1
        print "Total length:", total_length
        print "Not layed paths", not_layed_paths
        if not_used_chips != []:
            print "Deleted chips:", not_used_chips
        print paths
        Visualization.run3DVisualisation(paths)
        Visualization.runVisualization(paths)


def runAndSaveMultiple(run_amount):
    for i in range(run_amount):
        grid.clearGrid()
        seed = i
        random.seed(str(seed))

        global nets_unsorted, index_path_dict, conn_per_chip, conn_free_per_chip, not_used_chips, not_layed_paths, path_lay_amount
        nets_unsorted = []          # List with start and end points of lines
        index_path_dict = {}        # Dictionary with net-index as key and the path as value
        conn_per_chip = {}          # Dictionary with the number of
        conn_free_per_chip = {}
        not_used_chips = []
        not_layed_paths = []
        path_lay_amount = {}

        paths = main()
        if paths != []:
            total_length = 0
            for path in paths:
                total_length += len(path) - 1
            path_saver.saveToFile(paths, total_length, seed)


if __name__ == "__main__":
    #runMain()
    # If you comment out runMain() you can do some testing here
    runAndSaveMultiple(100)
