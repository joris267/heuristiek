import time
import numpy as np
import random
import data as Data
import Visualization
import grid as Grid
import itertools
import Controle
import copy

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


def checkIntsections(path_list):
    """
    Checks if there are intersections in the path.
    Returns the number of intersections in the path
    """
    chips = [str(chip) for chip in Data.chips]
    occurences_dict = {}
    joined_list = list(itertools.chain.from_iterable(path_list))
    for point in joined_list:
        if str(point) in occurences_dict:
            occurences_dict[str(point)] += 1
        else:
            occurences_dict[str(point)] = 1

    for point in occurences_dict:
        if occurences_dict[str(point)] > 1:
            if point not in chips:
                print "point", point, "is occupied by multiple lines"
                raise IntersectionError

    intersection_list = [i for i in occurences_dict.values() if i > 1]
    total_intersectios = sum(intersection_list)
    return total_intersectios


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


def moveHorizontal(x_start, x_end, y, layer, path_points):
    if x_start == x_end:
        i = 0
    else:
        direction = (x_end - x_start) / abs(x_end - x_start)  # left or right
        for i in range(direction, x_end - x_start + direction, direction):
            point = (x_start + i, y, layer)
            if isFree(point):
                path_points.append(point)
                setOccupation(point)
            else:
                i -= direction  # go to last occupied point
                break

    endpoint = (x_start + i, y, layer)
    return path_points, endpoint


def moveVertical(x, y_start, y_end, layer, path_points):
    if y_start == y_end:
        i = 0
    else:
        direction = (y_end - y_start) / abs(y_end - y_start)  # up or down
        for i in range(direction, y_end - y_start + direction, direction):
            point = (x, y_start + i, layer)
            if isFree(point):
                path_points.append(point)
                setOccupation(point)
            else:
                i -= direction  # go to last occupied point
                break

    endpoint =  (x, y_start + i, layer)
    return path_points, endpoint


def moveUpDPown(x, y, z_start, z_end, path_points):
    if z_start == z_end:
        i = 0
    else:
        direction = (z_end - z_start) / abs(z_end - z_start)  # above or below
        for i in range(direction, z_end - z_start + direction, direction):
            point = (x, y, z_start + i)
            if isFree(point):
                path_points.append(point)
                setOccupation(point)
            else:
                i -= direction  # go to last occupied point
                break

    endpoint = (x, y, z_start + i)
    return path_points, endpoint


def freeNeighbour(point):
    neighbours = []
    for dimension in range(3):
        for direction in range(-1, 2, 2):
            if point[2] == 7:
                if direction == 1 and dimension == 3:
                    continue
            list_point = list(point)
            list_point[dimension] += direction
            neighbour = tuple(list_point)
            if isFree(neighbour):
                neighbours.append(neighbour)
    return neighbours


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



def findPossiblePath(point1, point2, max_path_length = 60):
    """
    Finds a path between two points. Tries to move from one points towards the other point in the x, y and z directions.
    If this is not possible it moves to a random unoccupied neighbour. If there are no Free neighbours it raises a Stuckerror
    If the path is longer then max_path_length it raises a PathLengthError.
    """

    x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(point1, point2)
    start = (x_start, y_start, z_start)
    end = (x_end, y_end, z_end)
    setOccupation(end, True)

    occupied_points = len(findOccupiedPoints())

    path_points = [start]
    path_found = False
    current_point = start

    while not path_found:

        # try:

        if len(path_points) > max_path_length:
            # print "path to long"
            for point in path_points:
                setOccupation(point, True)
            raise PathLengthError()
        # except ValueError:
        #     print path_points
        #     assert False
        # randomizes the order in which a path wil be sought in the x, y and z direction
        dimensions = 2
        if current_point[2] != end[2]:
            dimensions += 1
        dimensions = range(dimensions)
        random.shuffle(dimensions)

        # to check if there is any way in which the path can move the current point is saved and compared at the end
        # of the search for the path in all directions
        last_point = current_point
        for random_dimension in dimensions:
            if random_dimension == 0:
                path_points, current_point = moveVertical(current_point[0], current_point[1], y_end, current_point[2], path_points)
            elif random_dimension == 1:
                path_points, current_point = moveHorizontal(current_point[0], x_end, current_point[1], current_point[2], path_points)
            else:
                path_points, current_point = moveUpDPown(current_point[0], current_point[1], current_point[2], z_end, path_points)

        # assert occupied_points + len(path_points) == len(findOccupiedPoints()) + 1  # start point is in both occupied_point and path_points

        if last_point == current_point:
            free_neighbours = freeNeighbour(current_point)
            if len(free_neighbours) == 0:
                # print "stuck"
                for point in path_points:
                    setOccupation(point, True)
                raise StuckError()
            current_point = random.choice(free_neighbours)
            path_points.append(current_point)
            setOccupation(current_point)

            # assert occupied_points + len(path_points) == len(findOccupiedPoints()) + 1

        if current_point == end:
            if sum([1 for point in path_points if point in chips]) != 2:  # only 1 point of the path is allowed to be on a chip
                print path_points
                print getPathOccupation((1,5,0))
                assert False
            return path_points, grid


def getDistance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def AStartAlgoritm(point1, point2, maxdept = 60, relay_badnes = 15):


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
    a_star_grid.fill([maxdept,range(len(netlist))])  # try to improve so have to start with global worse case senario

    temp_current_points = [point1]
    setAStarValue(point1, [0,[]])
    setOccupation(point2, True)
    setOccupation(point1, True)

    # On the start and end points the intersections don't count
    setPathOccupation(point1, -1)
    setPathOccupation(point2, -1)
    best_intersection_value, best_path_length = range(len(netlist)), maxdept
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

            raise AstarError
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


def findPaths(netlist, max_itterations = 1000, max_tries=2):
    """
    Tries to find the paths between al the chips in netlist
    """
    shortest_paths = {path_number: [] for path_number in range(len(netlist))}
    path_number = 0
    nets_layd = [False for net_number in range(len(netlist))]
    original_netlist = copy.deepcopy(netlist)
    itteration = -1
    path_tries = [0 for _ in netlist]
    while False in nets_layd:
        assert -1 not in shortest_paths
        itteration += 1
        if itteration == max_itterations:
            print path_tries
            break
        while nets_layd[path_number]:
            path_number += 1
            path_number = path_number % len(netlist)  # to keep cycling through the netlist

        net = netlist[path_number]
        path_tries[path_number] += 1
        path = []

        start, end = chips[net[0]], chips[net[1]]  # should not give error but I had trouble with this once.


        print "finding a path between %s and %s at the moment I have layed %i paths and am at itteration %i" %(start, end, len([i for i in nets_layd if i]), itteration)
        for point in chips:
            if getPathOccupation(point) != -2:
                print "het is", getPathOccupation(point), point
                assert False

        path = []
        # for _ in range(max_tries):
        #     try:
        #         path, grid = findPossiblePath(start, end)
        #         break
        #     except (PathLengthError, StuckError):
        #         setOccupation(start, False)
        #         setOccupation(end, False)

        if len(path) > 0:
            #smoothends path and corectelly sets occupation
            smoothened_path = Controle.smoothenPath(path)
            for point in path[1:-1]:
                if point not in smoothened_path:
                    setOccupation(point, True)
                else:
                    setPathOccupation(point, path_number)
            shortest_paths[path_number] = smoothened_path
            nets_layd[path_number] = True

        else:
            # print "path not found, trying Astar algorithm"
            path, conflicting_paths = AStartAlgoritm(start, end)
            try:
                conflicting_paths.remove(path_number)
                print "removing path ", path_number
            except:
                pass

            # realaying the conflicting paths
            for conflicting_path_number in conflicting_paths:
                conflicting_path = shortest_paths[conflicting_path_number]
                for point in conflicting_path[1:-1]:  # all points except the endpoints are free again
                    setOccupation(point, True)
                    setPathOccupation(point, -1)
                shortest_paths[conflicting_path_number] = []

            for point in path:
                setOccupation(point)
                setPathOccupation(point, path_number)
            setPathOccupation(start, -2)
            setPathOccupation(end, -2)

            shortest_paths[path_number] = path
            nets_layd[path_number] = True
            for conflicting_path in conflicting_paths:
                nets_layd[conflicting_path] = False
            # print "path found but paths %s will have to be refound" %(conflicting_paths)


        # extra check for intersections
        num_intersections = checkIntsections(shortest_paths.values())
        allowed_intersection_netlist = []
        for net_nummer in range(len(netlist)):
            if nets_layd[net_nummer]:
                allowed_intersection_netlist.append(netlist[net_nummer])
        allowed_intersections = doubleStartEndPoints(allowed_intersection_netlist)
        if allowed_intersections < num_intersections:
            print "program failed"
            print allowed_intersections, num_intersections
            print net, path
            print shortest_paths
            assert False

    print "The total wire length is %i from %i paths (from a total of %i)and there are %i intersections of which there are %i on the endpoints" % (
        calculateWireLenght(shortest_paths.values()), len([path for path in shortest_paths.values() if len(path) > 0]), len(original_netlist),
        num_intersections, allowed_intersections)
    return shortest_paths


if __name__ == "__main__":
    # constants
    # test = Data.e

    # chips = Data.chips
    # print set([(net[0], net[-1]) for net in test if len(net) > 1])
    # for net in test:
    #     for point in net[1:-1]:
    #         if point in chips:
    #             print point
    #             print net
    # print len([1 for path in test if len(path) > 1])
    # print checkIntsections(test)
    # import time
    # time.sleep(.2)
    # assert False

     for i in range(1):
        skips = 0
        X_SIZE = Data.X_SIZE
        Y_SIZE = Data.Y_SIZE
        Z_SIZE = Data.Z_SIZE
        chips = Data.chips
        netlist = Data.netlist
        netlist = Grid.sortDistance(netlist)

        path_grid = Grid.createPathGrid()
        grid = Grid.createGrid()
        relay_list = [0 for i in netlist]

        print 'finding paths'
        print netlist
        shortest_paths = findPaths(netlist, 2000, 1)
        print shortest_paths
        print skips


        aantal_paden_gelegd = len([path for path in shortest_paths.values() if len(path) > 0])
        totaal_paden = len(netlist)
        # safe output
        if True: #aantal_paden_gelegd == totaal_paden:
            Controle.safe(netlist, shortest_paths, relay_list)

        layer = 0
        Visualization.runVisualization(shortest_paths.values(), layer)