__author__ = 'Marcella Wijngaarden'

import data
import grid as Grid
import Visualization
import time
import random
import itertools
import numpy as np
import copy
#
# X_SIZE = data.X_SIZE
# Y_SIZE = data.Y_SIZE
# Z_SIZE = data.Z_SIZE
#
# chips = data.chips
# netlist = data.sortDistance(data.netlist)
# path_grid = grid.createPathGrid()
# grid = grid.createGrid()
# relay_list = [0 for i in netlist]
# skips = 0

def layIntersectingPaths():
    global grid

    paths = []
    intersection_paths = []
    paths_dict = {}
    path_number = 0
    temp_dict = {}

    print "Trying M method..."
    for net in netlist:
        start, end = chips[net[0]], chips[net[1]]
        original_value_start, original_value_end = isFree(start), isFree(end)
        x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(start, end)

        start = (x_start, y_start, z_start)
        end = (x_end, y_end, z_end)
        print "Finding a path between: ", start, end

        setPathOccupation(start, -2)
        setPathOccupation(end, -2)

        # path, grid = findPath(start, end, grid)
        path = []
        if len(path) == 0:
            paths_dict[path_number] = []
            intersection_paths.append(path_number)
            # temp_dict[path_number] = (start, end)
        else:
            for point in path:
                setPathOccupation(point, path_number)
                setOccupation(point)
            paths_dict[path_number] = path
            paths.append(path)

        path_number += 1
        setPathOccupation(start, -2)
        setPathOccupation(end, -2)

    # for chip in chips:
    #     setPathOccupation(chip, -2)

    # if len(temp_dict) > 0:
    #     print "Trying A* method.."
    #     # print getPathOccupation((13, 7, 0)), 1
    #     for item in temp_dict:
    #         start, end = temp_dict[item][0], temp_dict[item][1]
    #
    #         for chip in chips:
    #             if getPathOccupation(chip) != -2:
    #                 print chip, getPathOccupation(chip)
    #                 assert False
    #
    #         # print getPathOccupation((13, 7, 0)), 0
    #
    #         new_path, stuck_paths = AStartAlgoritm(start, end)[0], \
    #             AStartAlgoritm(start, end)[1]
    #
    #         for point in new_path:
    #             setPathOccupation(point, item)
    #             setOccupation(point, False)
    #
    #         # print getPathOccupation((13, 7, 0)), 3
    #         paths_dict[item] = new_path
    #         paths.append(new_path)
    #         setPathOccupation(start, -2)
    #         setPathOccupation(end, -2)
    #
    #         intersection_paths.append(item)
    #         for stuck in stuck_paths:
    #             intersection_paths.append(stuck)
            # print getPathOccupation((13, 7, 0)), 2

    print 'intersection paths : ', len(intersection_paths), intersection_paths
    print 'nr of paths drawn :', len(paths_dict)
    return intersection_paths, paths_dict

def isBetterPath(new_intersections, old_path_length, new_path_length, total_paths, iterations, totintersect):
    """
    Checks if a path should be constructed based on simulated annealing techniques.
    Returns True if the path should be constructed, otherwise returns False
    """

    if len(new_intersections) == 0:
        return True

    cross_value = (len(new_intersections) + 1)
    if old_path_length == 0:
        delta = 0
    else:
        delta = old_path_length - new_path_length

    weight = total_paths/float(len(netlist))
    # percentage = float(numpy.abs(float(numpy.cos(delta/ (float(cross_value)*weight))))) (-0.0013*iterations
    # percentage = float(numpy.abs(float(numpy.cos(delta/ (float(cross_value)*weight))))) (-0.0013*iterations

    percentage = float(np.exp((0.3 * delta)))/float((cross_value**0.8)) + (0.4 + 1/float(totintersect))
    chance = random.random()

    print 'chance = ', chance, 'percentage = ', percentage
    if chance < percentage:
        return True

    return False

def simulatedAnnealing(intersecting_paths, paths_dict, max_iteration=1000):
    counter = 0
    path_counter = 0
    step = 0
    paths_dict_new = paths_dict

    best_situation = {}
    best_situation_intersections = set()
    best_new_intersections = []
    intersecting_paths = set(intersecting_paths)

    print 'len intersecting paths ', intersecting_paths
    # for cross_path in intersecting_paths:
    #     for point in paths_dict_new[cross_path]:
    #         setOccupation(point)
    #         setPathOccupation(point, -1)
    #     paths_dict_new[cross_path] = []
    # print paths_dict_new
    # print netlist, netlist[0], netlist[49]
    finished = False
    found_50 = False
    while not finished:
        counter += 1
        #index = random.randrange(1, len(intersecting_paths))

        current_path_number = random.sample(intersecting_paths, 1)[0]
        #print current_path_number
        net = netlist[current_path_number]

        current_path = paths_dict_new[current_path_number]
        current_path_length = len(current_path)

        print 'current path number ', current_path_number, current_path
        for point in current_path:
            path_occupation = getPathOccupation(point)
            if path_occupation != -1 and path_occupation != -2 and path_occupation != current_path_number:
                print "Not correct : ", point, path_occupation
                assert False

        x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(chips[net[0]], chips[net[1]])
        start = (x_start, y_start, z_start)
        end = (x_end, y_end, z_end)

        for point in current_path[1:-1]:
            # print 'Resetting'
            setPathOccupation(point, -1)
            setOccupation(point, True)

        new_path, new_intersections_set = AStartAlgoritm(start, end)[0], \
                                          AStartAlgoritm(start, end)[1]

        for point in new_path:
            path_occupation = getPathOccupation(point)
            if path_occupation != -1 and path_occupation != -2 and path_occupation != current_path_number:
                if path_occupation not in new_intersections_set:
                    print "Not correct : ", point, path_occupation
                    new_intersections_set.add(path_occupation)

        if new_path[0] != end and new_path[-1] != start:
            print "Not finished path .. ", start, end, new_path[0], new_path[-1]
         #print new_path

        # setPathOccupation(start, -2)
        # setPathOccupation(end, -2)

        new_intersections = []
        if len(new_intersections_set) != 0:
            for item in new_intersections_set:
                new_intersections.append(item)

        print 'Iteration : ', counter
        if True:  # isBetterPath(new_intersections, current_path_length, len(new_path), len(paths_dict_new), counter, len(intersecting_paths)) or len(intersecting_paths) == 1 or len(intersecting_paths) == 2:
            path_counter += 1
            intersecting_paths.remove(current_path_number)
            paths_dict_new[current_path_number] = new_path
            # print 'relay path ', current_path_number

            for item in new_intersections_set:
                intersecting_paths.add(item)
                # if item not in intersecting_paths:
                #     if item == -2:
                #         print new_intersections_set, current_path_number
                #     if len(paths_dict_new[item]) != 0:
                for point in paths_dict_new[item][1:-1]:  # all points except the endpoints are free again
                    path_occupation = getPathOccupation(point)
                    if path_occupation != item and path_occupation != -1:
                        # print 'clearing point in path ', point, path_occupation
                        intersecting_paths.add(path_occupation)
                        for int_point in paths_dict_new[path_occupation]:
                            setOccupation(int_point, True)
                            setPathOccupation(int_point, -1)
                        if len(paths_dict_new[path_occupation]) != 0:
                            setOccupation(paths_dict_new[path_occupation][0], False)
                            setPathOccupation(paths_dict_new[path_occupation][0], -2)
                            setOccupation(paths_dict_new[path_occupation][-1], False)
                            setPathOccupation(paths_dict_new[path_occupation][-1], -2)
                            paths_dict_new[path_occupation] = []
                    setOccupation(point, True)
                    setPathOccupation(point, -1)
                if len(paths_dict_new[item]) != 0:
                    setPathOccupation(paths_dict_new[item][0], -2)
                    setPathOccupation(paths_dict_new[item][-1], -2)
                    setOccupation(paths_dict_new[item][0], False)
                    setOccupation(paths_dict_new[item][-1], False)
                    paths_dict_new[item] = []

            for point in new_path:
                path_occupation = getPathOccupation(point)
                if path_occupation != -1 and path_occupation != -2 and path_occupation != current_path_number:
                    # print "Not correct : ", point, path_occupation
                    intersecting_paths.add(path_occupation)
                    for int_point in paths_dict_new[path_occupation][1:-1]:
                        setOccupation(int_point, True)
                        setPathOccupation(int_point, -1)
                    if len(paths_dict_new[path_occupation]) != 0:
                        setOccupation(paths_dict_new[path_occupation][0], False)
                        setPathOccupation(paths_dict_new[path_occupation][0], -2)
                        setOccupation(paths_dict_new[path_occupation][-1], False)
                        setPathOccupation(paths_dict_new[path_occupation][-1], -2)
                        paths_dict_new[path_occupation] = []
                setOccupation(point, False)
                setPathOccupation(point, current_path_number)

            setPathOccupation(start, -2)
            setPathOccupation(end, -2)
            setOccupation(start, False)
            setOccupation(end, False)

            if found_50 is False:
                # Check if the total constructed paths is the best situation so far, if so remember it to return to
                # in case of stuck/too much decline
                if len(intersecting_paths) < len(best_situation_intersections) or path_counter == 1:
                    best_situation = paths_dict_new.copy()
                    best_situation_intersections = intersecting_paths.copy()
                    best_new_intersections = copy.deepcopy(new_intersections)
                    print 'New best situation : ', (len(best_situation)-len(best_situation_intersections))
                    step = 0
                elif len(intersecting_paths) == len(best_situation_intersections):
                    if len(new_intersections) < len(best_new_intersections):
                        best_situation = paths_dict_new.copy()
                        best_situation_intersections = intersecting_paths.copy()
                        best_new_intersections = copy.deepcopy(new_intersections)
                        print 'New best situation (less intersections) : ', (len(best_situation)-len(best_situation_intersections))
                        step = 0
                else:
                    step += 1
                    print 'step = ', step
                    # print 'Move on because ', len(intersecting_paths), 'intersections is more than ', \
                    #     len(best_situation_intersections)
                    if step >= 30:
                        step = 0
                        paths_dict_new = best_situation.copy()
                        intersecting_paths = best_situation_intersections.copy()
                        print 'Return to last best situation : ', len(best_situation)-len(best_situation_intersections)

            print "new_intersections ", len(new_intersections_set), "number of paths ", len(paths_dict_new), len(intersecting_paths), len(paths_dict_new) - len(intersecting_paths) #, new_intersections

        else:
            for point in current_path[1:-1]:
                setPathOccupation(point, current_path_number)
                setOccupation(point, False)
            setPathOccupation(start, -2)
            setOccupation(start, False)
            setPathOccupation(end, -2)
            setOccupation(end, False)

        if len(intersecting_paths) == 0:
            print paths_dict_new
            return paths_dict_new

        if counter == max_iteration:
            print "No solution.. "
            return paths_dict_new

def getTotalLength(paths):
    total = 0
    for path in paths:
        total += len(path)

    return total

####################################################################################################
########################################################################################


class PathLengthError(Exception):
    def __init__(self):
        pass


class StuckError(Exception):
    def __init__(self):
        pass

class AstarError(Exception):
    def __init__(self):
        pass

class IntersectionError(Exception):
    def __init__(self):
        pass

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


def checkIntsections(path_dict):
    """
    Checks if there are intersections in the path.
    Returns the number of intersections in the path
    """

    path_list = path_dict.values()
    chips = data.chips
    intersections = []

    list_of_points = []
    for path in path_list:
        for point in path:
            list_of_points.append(point)

    for point in list_of_points:
        occurences = list_of_points.count(point)
        if occurences > 1:
            if point not in chips:
                path_nr = getPathOccupation(point)
                print point, occurences, path_nr
                if path_nr == -1:
                #     print "path_nr = ", path_nr, point
                    continue

                intersections.append(path_nr)
                for points in paths_dict[path_nr][1:-1]:
                    setOccupation(points, True)
                    setPathOccupation(points, -1)

    return intersections



def doubleStartEndPoints(netlist, chip_to_occurrences=None):
    """
    Find the number of double start/end points, that is, the sum of al occurrences higher then 1.
    """
    som = 0
    if chip_to_occurrences is None:
        chips_in_netlist = list(itertools.chain.from_iterable(netlist))
        occurrences = np.bincount(chips_in_netlist)
        for i in occurrences:
            if i > 1:
                som += i

    else:
        for connection in chip_to_occurrences.values():
            if connection > 1:
                som += 1

    return som


def isFree(point):
    """
    For a given point (x,y,z) returns True if occupied, else False
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
    return value


def setOccupation(point, occupation = False):
    """
    For a given point changes it's value in the grid to the given occupation.
    Returns nothing.
    """
    grid[point[0]][point[1]][point[2]] = occupation


def setPathOccupation(point, path_number):
    """
    For a given point changes it's value in the path grid to the path number
    Returns nothing.
    """
    path_grid[point[0]][point[1]][point[2]] = path_number


def getPathOccupation(point):
    """
    returns path number present on point, return -1 if no path on point
    """
    return path_grid[point[0]][point[1]][point[2]]


def calculateEndStart(start, end):
    x_start = min([start[0], end[0]])
    if x_start == start[0]:
        x_end = end[0]
        y_start = start[1]
        y_end = end[1]
        z_start = start[2]
        z_end = end[2]
    else:
        x_end = start[0]
        y_start = end[1]
        y_end = start[1]
        z_start = end[2]
        z_end = start[2]

    return x_start, x_end, y_start, y_end, z_start, z_end

def inGrid(point):
    return (0 <= point[0] < X_SIZE) and (0 <= point[1] < Y_SIZE ) and (0 <= point[2] < Z_SIZE)


def findNeighbours(point):
    neighbours = []
    for dimension in range(3):
        for direction in range(-1, 2, 2):
            if point[2] == 7:
                if direction == 1 and dimension == 3:
                    continue
            list_point = list(point)

            list_point[dimension] += direction
            neighbour = tuple(list_point)
            if inGrid(neighbour):
                neighbours.append(neighbour)
    return neighbours


def findOccupiedPoints():
    occupied_points = []
    for z in range(len(grid[0][0])):
        for y in range(len(grid[0])):
            for x in range(len(grid)):
                if not isFree((x,y,z)):
                    occupied_points.append((x,y,z))

    # print len(occupied_points), len([1 for  z in grid for y in z for x in y if not x])
    return occupied_points

def getDistance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def AStartAlgoritm(point1, point2, maxdept =60, relay_badnes=15):


    def setAStarValue(point, value):
        # try:
        if inGrid(point):
            a_star_grid[point[0]][point[1]][point[2]] = value
        # except:
        #     print point[0]


    def getAStarValue(point):
        if inGrid(point):
            return a_star_grid[point[0]][point[1]][point[2]]
        else:
            raise AstarError


    def getIntersectionValuePathLength(value_point):

        point_path_length = value_point[0]
        # intersection_value_point = len(value_point[1])
        intersection_value_point =  0
        for intersectiong_path in set(value_point[1]):
            intersection_value_point += 1 + relay_list[intersectiong_path] / relay_badnes

        return intersection_value_point, point_path_length


    a_star_grid = np.ndarray(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=list)

    #grid is filled with list [number, set with conflicts]
    a_star_grid.fill([maxdept, range(len(netlist))])  # try to improve so have to start with global worse case senario

    temp_current_points = [point1]
    setAStarValue(point1, [0,[]])
    setOccupation(point2, True)
    setOccupation(point1, True)

    # On the start and end points the intersections don't count
    setPathOccupation(point1, -1)
    setPathOccupation(point2, -1)
    best_intersection_value, best_path_length = maxdept, range(len(netlist))
    setAStarValue(point1, [0,[]])
    # print "at start itteration: ", getPathOccupation((1,5,0))

    global skips
    for itteration in range(maxdept):
        # print "going down deeper, itteration %i, we have %i points to move" %(itteration, len(temp_current_points))
        current_points = set(temp_current_points)
        temp_current_points = []

        for point in current_points:
            neighbours = findNeighbours(point)
            try:
                value = getAStarValue(point)
            except:
                print point
                assert False

            value[0] += 1  # taking a step
            for neighbour in neighbours:
                AStar_value = copy.deepcopy(value)

                if not isFree(neighbour):
                    intersectiong_path = getPathOccupation(neighbour)
                    if intersectiong_path == -2:  # if the point is occupied by a chip we can skip it
                        continue

                    AStar_value[1].append(intersectiong_path)

                # has to be here because intersections happens just above


                intersection_value_current_point, path_length_current_point = getIntersectionValuePathLength(AStar_value)
                if intersection_value_current_point > best_intersection_value:
                    skips += 1
                    continue
                elif intersection_value_current_point == best_intersection_value and path_length_current_point > best_path_length:
                    skips += 1
                    continue
                else:
                    pass  # worthy candidate


                intersection_value_neighbour, path_length_neighbour = getIntersectionValuePathLength(getAStarValue(neighbour))
                if intersection_value_neighbour > intersection_value_current_point:  # so if move gives a better result
                    setAStarValue(neighbour, AStar_value)
                    temp_current_points.append(neighbour)
                    if neighbour == point2:
                        best_intersection_value, best_path_length = intersection_value_current_point, path_length_current_point
                elif intersection_value_neighbour == intersection_value_current_point and path_length_neighbour > path_length_current_point:
                    setAStarValue(neighbour, AStar_value)
                    temp_current_points.append(neighbour)
                    if neighbour == point2:
                        best_intersection_value, best_path_length = intersection_value_neighbour, path_length_neighbour
                # print getAStarValue(neighbour)
            # print Controle.getAvrgValueAStarDistance(a_star_grid)
            # assert False

    assert itteration == maxdept - 1
    final_astar_path = [point2]
    current_point = point2
    best_neigbour = current_point

    # print "when going back", getPathOccupation((1,5,0))

    while current_point != point1:
        intersection_value_current_point, path_length_current_point = getIntersectionValuePathLength(getAStarValue(current_point))
        # best_neigbours = []
        for neighbour in findNeighbours(current_point):
            intersection_value_neighbour, neighbour_path_length =  getIntersectionValuePathLength(getAStarValue(neighbour))

            if intersection_value_neighbour > intersection_value_current_point:
                continue  # skipp it to improve speed
            elif intersection_value_neighbour < intersection_value_current_point:
                best_neigbour = neighbour
            elif intersection_value_neighbour == intersection_value_current_point and neighbour_path_length < path_length_current_point:
                best_neigbour = neighbour
            elif intersection_value_neighbour == intersection_value_current_point and neighbour_path_length \
                    == path_length_current_point and random.random() > .5:
                best_neigbour = neighbour

        if best_neigbour == current_point:  # check to see if a best neighbour is found
            print current_point
            print len(getAStarValue(current_point)[1]), getAStarValue(current_point)[0]
            print point1, point2
            print [(len(getAStarValue(i)[1]), getAStarValue(i)[0]) for i in findNeighbours(current_point)]
            return [], set([])
        else:
            # best_neigbour = random.choice(best_neigbours)
            final_astar_path.append(best_neigbour)
            current_point = best_neigbour

    conflicting_paths = []
    for point in final_astar_path:
        conflicting_paths.append(getPathOccupation(point))
    conflicting_paths = set(conflicting_paths)
    if -1 in conflicting_paths:
        conflicting_paths.remove(-1)

    for path_number in conflicting_paths:
        relay_list[path_number] += 1

    if sum([1 for point in final_astar_path if point in chips]) != 2:  # only 1 point of the path is allowed to be on a chip
        print final_astar_path
        assert False
    return final_astar_path, conflicting_paths

def checkConnections(first_point, second_point, path):

    current_length = len(path)
    #check if the points are on one line
    delta_x = abs(max(first_point[0], second_point[0]) - min(first_point[0], second_point[0]))
    delta_y = abs(max(first_point[1], second_point[1]) - min(first_point[1], second_point[1]))
    delta_z = abs(max(first_point[2], second_point[2]) - min(first_point[2], second_point[2]))

    # delta_x = abs(first_point[0] - second_point[0])
    # delta_y = abs(first_point[1] - second_point[1])
    # delta_z = abs(first_point[2] - second_point[2])

    setOccupation(second_point, True)

    combo = [delta_x, delta_y, delta_z]
    not_zero = []
    i = 0
    for delta in combo:
        if delta != 0:
            not_zero.append([delta, i])
        i += 1


    track = []
    if len(not_zero) == 1:
        # print 'look between : ', first_point, second_point
        # print 'current path : ', path
        delta = not_zero[0][0]
        dimension = not_zero[0][1]  # move in x, y or z direction
        direction = -(first_point[dimension] - second_point[dimension])/delta

        if direction != 0:
            for j in range(0, direction*(delta+2), direction):
                check_point_list = [first_point[0], first_point[1], first_point[2]]
                check_point_list[dimension] = check_point_list[dimension] + j
                check_point = (check_point_list[0], check_point_list[1], check_point_list[2])
                if isFree(check_point) or check_point in path:
                    track.append(check_point)
                    # print 'track = ', track
                    if check_point == second_point and len(track) < current_length:
                        if track != path:
                            setOccupation(second_point, False)
                            # print 'track returned'
                            return track
                        else:
                            break
                    else:
                        continue
                else:
                    setOccupation(second_point, False)
                    return None

    setOccupation(second_point, False)
    return None

def superSmoothPath(path):

    old_path = path
    i = 0
    print 'begin'
    while i < len(path):
        point = path[i]
        j = 1
        while j < len(path):
            other_point = path[j]
            connection_path = path[i:(j+1)]
            connections = checkConnections(point, other_point, connection_path)
            if connections is not None:
                # print 'finding path between :', path[0], path[-1]
                # print 'point : ', point, 'other_point : ', other_point
                pre_path = path[:i]
                post_path = path[(j+1):]
                path = [pre_path + connections + post_path][0]
                j = 0
                # print "connection path old: ", connection_path
                # print 'pre_path = ', pre_path, 'connections = ', connections, 'post_path = ', post_path, 'path = ', path
                # # break
            j += 1
        i += 1

    if old_path != path:
        for point in path:
            setOccupation(point, False)
        for point in old_path:
            if point not in path:
                setOccupation(point, True)

    return path


if __name__ == "__main__":
    skips = 0
    X_SIZE = data.X_SIZE
    Y_SIZE = data.Y_SIZE
    Z_SIZE = data.Z_SIZE
    chips = data.chips
    netlist = data.netlist
    netlist = Grid.sortDistance(netlist)
    relay_list = [0 for i in netlist]

    path_grid = Grid.createPathGrid()
    grid = Grid.createGrid()
    start_time = time.time()
    comp = layIntersectingPaths()
    intersecting_paths, paths_dict = comp[0], comp[1]
    paths = simulatedAnnealing(intersecting_paths, paths_dict, max_iteration=1800)
    end_time = time.time()
    total_length = calculateWireLenght(paths.values())

    print paths
    print "Total wire length = ", total_length, "Computing time = ", end_time - start_time, " seconds or ", (end_time - start_time)/60, "minutes"

    Visualization.runVisualization(paths.values(), 0)
    Visualization.run3DVisualisation(paths.values(), 0)

    smoothed_paths = []
    for path in paths.values():
        smoothed_paths.append(superSmoothPath(path))

    total_length = calculateWireLenght(smoothed_paths)

    print smoothed_paths
    print "Total wire length = ", total_length, "Computing time = ", end_time - start_time, " seconds or ", (end_time - start_time)/60, "minutes"

    Visualization.runVisualization(smoothed_paths, 0)
    Visualization.run3DVisualisation(smoothed_paths, 0)


