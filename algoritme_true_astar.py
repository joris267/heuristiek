import copy
import path_saver
import random
import time
import data
import grid_copy as grid
from heapq import *
import Visualization
import numpy

seed = 10
random.seed(str(seed))
chips = data.chips
netlist = data.netlist_1
print "Netlist size:", len(netlist)

data_grid = grid.grid

img_no = 0
nets_unsorted = []          # List with start and end points of lines
index_path_dict = {}        # Dictionary with net-index as key and the path as value
conn_per_chip = {}          # Dictionary with the number of
conn_free_per_chip = {}
not_used_chips = []
not_layed_paths = []
path_lay_amount = {}
visualise_dict = {}
netlist_sorted = []
hillclimber_visualisation = [[], []]



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
        print "Not used chips:", not_used_chips
        print "Delete chip from chiplist..."
        if len(conn_per_chip.keys()) != len(chips) - len(not_used_chips):
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
        if neighbour in chips and neighbour not in not_used_chips:
            neighbour_chips.append(neighbour)
    return neighbour_chips


def aStar(point1, point2, line_val, mode="no_intersections", chip_neighbour="keep_free"):
    """
    mode: to allow intersections or not (it will find a path with the least amount of intersections)
    chip_neighbour: to ignore or keep free the neighbours of chips that are not the end or begin point
    return: a path if one is found, an empty list if nothing is found (only possible in mode 'no_intersection')
    """
    global conn_free_per_chip
    queue = []  # (f, g, h, point, path_to_point, conn_free_per_chip), point = (x, y, z)
    g = 0
    h = grid.minPathLength((point1, point2))
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
            h = grid.minPathLength((successor, point2))
            f = g + h
            if mode == "with_intersections" and grid.isOccupied(successor):
                if grid.getPointOccupation(successor) != -2:
                    g += 50 * path_lay_amount[grid.getPointOccupation(successor)]
                    f = g + h
            if mode == "no_intersections" and grid.isOccupied(successor):
                continue
            if chip_neighbour == "keep_free":
                if successor in chips_neighbours:                # Paths are allowed to have a path next to a chip
                    valid = True                                 # which isn't the start or end points
                    for chip in getNeighbourChips(successor):    # BUT: only when there are unused spots available for
                        if conn_free_per_chip[chip] <= 0:        # that particular chip; chips don't always use their
                            valid = False                        # maximum available free spots
                            break                                #
                        else:                                    #
                            conn_free_copy = copy.deepcopy(conn_free_per_chip)
                            conn_free_copy[chip] -= 1            #
                            g += 50                              # Avoid laying a line next to a chip, but its possible
                            f = g + h                            # Therefore a penalty of 50 is given
                    if not valid:                                #
                        continue                                 #
            if chip_neighbour == "ignore":
                pass
            item = (f, g, h, successor, q[4] + [successor], conn_free_copy)
            heappush(queue, item)

    print "Path not found for:", line_val, "Points:", point1, point2
    not_layed_paths.append((line_val, (point1, point2)))
    return []


def main():
    global netlist_sorted, img_no, index_path_dict, not_layed_paths

    print "\n### Starting A* ###"
    initialise()
    netlist_sorted = sorted(nets_unsorted, key=grid.minPathLength)  # Sort nets_unsorted by minimum length
    for chip in conn_per_chip.keys():
        free = len(findNeighbours(chip)) - conn_per_chip[chip]
        conn_free_per_chip[chip] = free
    for index, net in enumerate(netlist_sorted):
        path = aStar(net[0], net[1], index)
        if path != []:
            index_path_dict[index] = path
            visualise_dict[index] = path
            #Visualization.run3DVisualisation(visualise_dict.values(), img_no)  # For making a movie
            img_no += 1
            grid.setOccupation(path, index)

    print "No of paths layed:", len(netlist) - len(not_layed_paths)

    #################################################################################################
    ### All paths that could have been placed are placed, but some paths cannot be placed because ###
    ### other paths are in the way. The next section cuts away blocking paths.                    ###
    #################################################################################################

    print "\n### Starting A* with intersections ###"
    total_length = layRemainingPaths(index_path_dict, chip_neighbour="keep_free")
    print "Total length:", total_length

    ########################################################
    ### At this point all paths should have been placed  ###
    ### Time for hillclimber to optimize path length     ###
    ########################################################

    print "\n### Starting Hillclimber method ###"
    best_index_path_dict = index_path_dict.copy()
    best_total_length = total_length
    iterations_not_changed = 0
    iteration = 0
    temperature = 1.
    while iterations_not_changed < 1500:
        hillclimber_visualisation[0].append(iteration)
        hillclimber_visualisation[1].append(best_total_length)
        iteration += 1
        iterations_not_changed += 1
        if iteration % 250 == 0:
            print "Iteration:", iteration
        if best_index_path_dict != index_path_dict:
            raise StandardError
        checkPathDict(index_path_dict, iteration)
        for path in best_index_path_dict.values():
            if path == []:
                raise StandardError
        if len(best_index_path_dict.values()) != len(netlist):
            raise StandardError
        # Choose 3 different paths to be cut away
        path_1 = random.choice(index_path_dict.keys())
        path_2 = random.choice(index_path_dict.keys())
        path_3 = random.choice(index_path_dict.keys())
        while path_1 == path_2 or path_2 == path_3 or path_1 == path_3:
            path_2 = random.choice(index_path_dict.keys())
            path_3 = random.choice(index_path_dict.keys())
        remove_paths = [path_1, path_2, path_3]
        #print "Remove:", remove_paths
        for path in remove_paths:
            grid.clearOccupation(index_path_dict[path])
            del index_path_dict[path]
            not_layed_paths.append((path, netlist_sorted[path]))
        index_path_dict_copy = index_path_dict.copy()
        #new_total_length = layRemainingPaths(index_path_dict, chip_neighbour="ignore")
        new_total_length = layRemainingPaths(index_path_dict_copy, max_iteration=50, chip_neighbour="keep_free")
        if new_total_length == []:
            not_layed_paths = []
            index_path_dict = best_index_path_dict.copy()
            grid.rebuildGrid(best_index_path_dict)
            continue
        index_path_dict = index_path_dict_copy.copy()

        ### Simulated Annealing ### Uncomment for hillclimber
        if 1000 < iteration < 5000:             # Cool down between 1000 and 5000 iterations
            temperature = 1. - iteration/5000.
        elif iteration >= 5000:                 # Don't divide by 0 and temperature has to remain positive
            temperature = 0.0000001             # This is practically a hillclimber from now on
        difference = new_total_length - best_total_length
        if numpy.exp(-(0.15/temperature) * difference) > random.random():
            # Path is accepted
            if new_total_length != best_total_length:
                print "New length:", new_total_length
                iterations_not_changed = 0
            best_index_path_dict = index_path_dict.copy()
            best_total_length = new_total_length
        else:
            # Path is not accepted
            index_path_dict = best_index_path_dict.copy()
        ### \Simulated Annealing ###

        ### Hillclimber ### Uncomment for simulated annealing
        #if new_total_length < best_total_length:
        #     print "New Best length:", new_total_length
        #     iterations_not_changed = 0
        #     best_index_path_dict = index_path_dict.copy()
        #     best_total_length = new_total_length
        #else:
        #     index_path_dict = best_index_path_dict.copy()
        ### \Hillclimber ###

        grid.rebuildGrid(best_index_path_dict)

    return best_index_path_dict.values()


def layRemainingPaths(path_dict, max_iteration=5000, chip_neighbour="keep_free"):
    global img_no
    iteration = 0
    while not_layed_paths != []:
        iteration += 1
       #print "Iteration:", iteration
        #print "Paths placed:", len(netlist) - len(not_layed_paths)
        if iteration == max_iteration:
            print "Could not find solution"
            return []
        index, net = random.choice(not_layed_paths)
        #print "Path " + str(index) + ":", net
        path = aStar(net[0], net[1], index, mode="with_intersections", chip_neighbour=chip_neighbour)
        visualise_dict[index] = path
        intersections = grid.getOccupation(path)
        for intersection in intersections:
            path_lay_amount[intersection] += 1
            visualise_dict[intersection] = []
            grid.clearOccupation(path_dict[intersection])
            del path_dict[intersection]
            not_layed_paths.append((intersection, netlist_sorted[intersection]))

        not_layed_paths.remove((index, net))
        grid.setOccupation(path, index)
        path_dict[index] = path
        #Visualization.run3DVisualisation(visualise_dict.values(), img_no)  # For making a movie
        img_no += 1
    total_length = 0
    for path in path_dict.values():
        total_length += len(path) - 1

    return total_length


def checkPathDict(path_dict, iteration):
    points_occupied = []
    paths = path_dict.keys()
    for path in paths:
        for point in path_dict[path]:
            if point in points_occupied and point not in chips:
                print "Point", point
                print "Path no", path
                print "Iteration", iteration
                Visualization.runVisualization(path_dict.values())
                raise StandardError
            else:
                points_occupied.append(point)


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
        start = time.clock()
        grid.clearGrid()
        seed = i
        random.seed(str(seed))

        global img_no, nets_unsorted, index_path_dict, conn_per_chip, conn_free_per_chip, not_used_chips, \
            not_layed_paths, path_lay_amount, visualise_dict, netlist_sorted, hillclimber_visualisation
        img_no = 0
        nets_unsorted = []          # List with start and end points of lines
        index_path_dict = {}        # Dictionary with net-index as key and the path as value
        conn_per_chip = {}          # Dictionary with the number of
        conn_free_per_chip = {}
        not_used_chips = []
        not_layed_paths = []
        path_lay_amount = {}
        visualise_dict = {}
        netlist_sorted = []
        hillclimber_visualisation = [[], []]

        paths = main()
        if paths != []:
            total_length = 0
            for path in paths:
                total_length += len(path) - 1
            path_saver.saveToFile(paths, total_length, seed)
        Visualization.hillclimberVisualisation(hillclimber_visualisation, seed)
        print "Calculated in:", time.clock() - start


if __name__ == "__main__":
    #runMain()
    runAndSaveMultiple(1000)
    # If you comment out runMain() and/or runAndSaveMultiple() you can do some testing here
