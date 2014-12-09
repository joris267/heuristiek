import time
import numpy as np
import random
import data as Data
import Visualization
import grid as Grid
import itertools
import Controle
import copy
import netlist_checker

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

class outOfGrid(Exception):
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
    global chips
    local_chips = [str(chip) for chip in chips]
    occurences_dict = {}
    joined_list = list(itertools.chain.from_iterable(path_list))
    for point in joined_list:
        if str(point) in occurences_dict:
            occurences_dict[str(point)] += 1
        else:
            occurences_dict[str(point)] = 1

    for point in occurences_dict:
        if occurences_dict[str(point)] > 1:
            if point not in local_chips:
                print "point", point, "is occupied by multiple lines"
                print local_chips
                point = point.split(",")
                point = (int(point[0][1:]), int(point[1]), int(point[2][:-1]))
                for path in path_list:
                    if point in path:
                        print "it is in path: ", path
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
                setOccupation(point)
                path_points.append(point)
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
                setOccupation(point)
                path_points.append(point)
            else:
                i -= direction  # go to last occupied point
                break

    endpoint =  (x, y_start + i, layer)
    return path_points, endpoint


def moveUpDown(x, y, z_start, z_end, path_points):
    if z_start == z_end:
        i = 0
    else:
        direction = (z_end - z_start) / abs(z_end - z_start)  # above or below
        for i in range(direction, z_end - z_start + direction, direction):
            point = (x, y, z_start + i)
            if isFree(point):
                setOccupation(point)
                path_points.append(point)
            else:
                i -= direction  # go to last occupied point
                break

    endpoint = (x, y, z_start + i)
    return path_points, endpoint


def createNeighbourGrid():
    """
    Creates a grid filled with list of neighbouring chip indices
    imports chips, X_SIZE, Y_SIZE and Z_SIZE from data
    """
    neighbour_grid = np.ndarray(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype = list)
    neighbour_grid.fill(-1)
    for chip in chips:
        neighbour_grid[chip[0]][chip[1]][chip[2]] = -2
    for chip, chip_index in zip(chips, range(len(chips))):
        # print algoritme.freeNeighbour(chip)
        for neighbour in freeNeighbour(chip):
            if neighbour_grid[neighbour[0]][neighbour[1]][neighbour[2]] == -2:
                continue
            elif neighbour_grid[neighbour[0]][neighbour[1]][neighbour[2]] == -1:
                neighbour_grid[neighbour [0]][neighbour[1]][neighbour[2]] = [chip_index]
            else:
                neighbour_grid[neighbour[0]][neighbour[1]][neighbour[2]].append(chip_index)


    return neighbour_grid


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



def findPossiblePath(point1, point2, max_path_length, max_times_almost_stuck):
    """
    Finds a path between two points. Tries to move from one points towards the other point in the x, y and z directions.
    If this is not possible it moves to a random unoccupied neighbour. If there are no Free neighbours it raises a Stuckerror
    If the path is longer then max_path_length it raises a PathLengthError.
    """
    global iteration
    x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(point1, point2)
    start = (x_start, y_start, z_start)
    end = (x_end, y_end, z_end)
    setOccupation(end, True)
    path_points = [start]
    path_found = False
    current_point = start
    times_almost_stuck = 0

    while not path_found:
        if len(path_points) > max_path_length:
            raise PathLengthError()

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
                path_points, current_point = moveUpDown(current_point[0], current_point[1], current_point[2], z_end, path_points)

        #  If there is no way to move towards the end point take a step in a random direction
        if last_point == current_point:
            free_neighbours = freeNeighbour(current_point)
            if len(free_neighbours) == 0 or times_almost_stuck > max_times_almost_stuck:
                raise StuckError()

            current_point = random.choice(free_neighbours)
            if current_point not in path_points:
                times_almost_stuck += 1
                setOccupation(current_point)
                path_points.append(current_point)


        if current_point == end:
            if sum([1 for point in path_points if point in chips]) != 2:  # only 1 point of the path is allowed to be on a chip
                print path_points
                assert False
            return path_points


def getDistance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def getNeighbourGridValue(point, start, end):
    """
    Checks if occupieing this point would rob a point of his options to do a first step, if true then this returns False
    If the move can be made this function returns True
    """

    neighbour_value = neighbour_grid[point[0]][point[1]][point[2]]
    if neighbour_value == -2: # if neighbour is a chip we cant go there
        return False
    elif neighbour_value == -1:  # if neighbour is not next to a chip we def. can go there
        return True
    else:
        for chip_index in neighbour_value:
            if chip_index == start or chip_index == end:
                continue
            if len(freeNeighbour(point)) - 1 < connections_per_chip[chip_index]:  # it it would be occupied there would be one less free neighbour
                return False
    return True



def AStartAlgoritm(start, end, maxdept, relay_badnes, skips_is_aan = False):


    def setAStarValue(point, value):
        if inGrid(point):
            a_star_grid[point[0]][point[1]][point[2]] = value


    def getAStarValue(point):
        if inGrid(point):
            return a_star_grid[point[0]][point[1]][point[2]]
        else:
            raise outOfGrid


    def getIntersectionValuePathLength(value_point):
        point_path_length = value_point[0]
        intersection_value_point =  0
        for intersectiong_path in set(value_point[1]):
            # if relay_list[intersectiong_path] > 20:
            #     return 200, point_path_length
            intersection_value_point += 1 + relay_list[intersectiong_path] / relay_badnes

        return intersection_value_point, point_path_length


    global skips, itteration
    a_star_grid = np.ndarray(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=list)
    a_star_grid.fill([maxdept+1,range(len(netlist))])  # grid is filled with list [path length, set with conflicts]
    point1, point2 = chips[start], chips[end]
    temp_current_points = [point1]
    setAStarValue(point1, [0,[]])
    setOccupation(point2, True)
    setOccupation(point1, True)

    # On the start and end points the intersections don't count
    setPathOccupation(point1, -1)
    setPathOccupation(point2, -1)
    best_intersection_value, best_path_length = maxdept, range(len(netlist))
    setAStarValue(point1, [0,[]])
    possible_path_found = False
    const_skip = 0

    for astar_itteration in range(maxdept):
        # print "going down deeper, itteration %i, we have %i points to move" %(astar_itteration, len(temp_current_points))
        current_points = set(temp_current_points)
        temp_current_points = []


        # for every point on the surface on the sphere we try to moves
        for point in current_points:
            neighbours = findNeighbours(point)
            value = getAStarValue(point)


            value[0] += 1  # taking a step
            for neighbour in neighbours:


                # start of multiple checks to discard options that are not good
                AStar_value = copy.deepcopy(value)

                # if the point is not free and it is a chip we cant use it otherwise it is an extra intersection
                if not isFree(neighbour):
                    intersectiong_path = getPathOccupation(neighbour)
                    if intersectiong_path == -2:
                        continue
                    else:
                        AStar_value[1].append(intersectiong_path)

                # if it is a free point but we would rid a chip of to manny of its remaining start options we cant sue it doesn't work atm
                if skips_is_aan:

                    if neighbour[2] < 2 and neighbour != point2:  # only in the bottom two layers we must reserve neighbours
                        if not getNeighbourGridValue(neighbour, start, end):
                            const_skip += 1
                            continue

                # If current path length is less then worst path length we cant use it.
                intersection_value_current_point, path_length_current_point = getIntersectionValuePathLength(AStar_value)
                if intersection_value_current_point > best_intersection_value:
                    skips += 1
                    continue
                elif intersection_value_current_point == best_intersection_value and path_length_current_point > best_path_length:
                    skips += 1
                    continue
                else:
                    pass

                # End of checks, if program reaches this point the move may be worth and we proceed to checks if the move
                # would improve the situation
                intersection_value_neighbour, path_length_neighbour = getIntersectionValuePathLength(getAStarValue(neighbour))
                if (intersection_value_neighbour > intersection_value_current_point) or \
                        (intersection_value_neighbour == intersection_value_current_point and path_length_neighbour > path_length_current_point):
                    setAStarValue(neighbour, AStar_value)
                    temp_current_points.append(neighbour)

                    # if the move is made and we reach the end point we can discard all paths that are worse then what we
                    # found uptil now.
                    if neighbour == point2:
                        possible_path_found = True
                        best_intersection_value, best_path_length = intersection_value_current_point, path_length_current_point


    # print const_skip
    # now we have created a big sphere and we have to find the best path back.
    final_astar_path = [point2]
    current_point = point2
    assert getAStarValue(point2)[0]>1
    best_neigbour = current_point
    if not possible_path_found:
        raise AstarError

    i = 0
    while current_point != point1:
        intersection_value_current_point, path_length_current_point = getIntersectionValuePathLength(getAStarValue(current_point))
        for neighbour in findNeighbours(current_point):
            intersection_value_neighbour, neighbour_path_length =  getIntersectionValuePathLength(getAStarValue(neighbour))

            if intersection_value_neighbour > intersection_value_current_point:
                continue  # skipp it to improve speed
            elif intersection_value_neighbour < intersection_value_current_point or \
                    (intersection_value_neighbour == intersection_value_current_point and neighbour_path_length < path_length_current_point):
                best_neigbour = neighbour

            # if multiple neighbours are god options this gives them a equall chance to be selected.
            # if there are often more then 2 neighbours with equal value this gives a bias. In our tests the induced
            # bias was very small (never more then 3 neighbours with same value)
            elif intersection_value_neighbour == intersection_value_current_point and neighbour_path_length \
                    == path_length_current_point and random.random() > .5:
                best_neigbour = neighbour

        if best_neigbour == current_point:  # If the best neighbour is the current point we havent moved so something is wrong
            i += 1
            if i == 1:
                print current_point
                print len(getAStarValue(current_point)[1]), getAStarValue(current_point)[0]
                print point1, point2
                print [(getAStarValue(i)[0], len(getAStarValue(i)[1]), getAStarValue(i)[1]) for i in findNeighbours(current_point)]

                raise AstarError
        else:
            final_astar_path.append(best_neigbour)
            current_point = best_neigbour


    # find all the conflicting paths
    conflicting_paths = []
    for point in final_astar_path:
        conflicting_paths.append(getPathOccupation(point))
    conflicting_paths = set(conflicting_paths)
    if -1 in conflicting_paths: # -1 means it was free so not a real path value
        conflicting_paths.remove(-1)


    for path_number in conflicting_paths:
        relay_list[path_number] += 1

    # extra check to check if none of the path points besides te start and end point are on a chip
    if sum([1 for point in final_astar_path if point in chips]) != 2:
        print final_astar_path
        assert False

    return final_astar_path, conflicting_paths






def _find_path_overide(start, end):
    """
    finds the shortest path and lays it and returns intersections
    """
    def moveHorizontal_overide(x_start, x_end, y, layer, path_points):
        if x_start == x_end:
            pass
        else:
            direction = (x_end - x_start) / abs(x_end - x_start)  # left or right
            for i in range(direction, x_end - x_start + direction, direction):
                point = (x_start + i, y, layer)
                path_points.append(point)

        return path_points


    def moveVertical_overide(x, y_start, y_end, layer, path_points):
        if y_start == y_end:
            pass
        else:
            direction = (y_end - y_start) / abs(y_end - y_start)  # up or down
            for i in range(direction, y_end - y_start + direction, direction):
                point = (x, y_start + i, layer)
                path_points.append(point)

        return path_points

    x1, y1, z1 = chips[start]
    x2, y2, z2 =  chips[end]
    z1 += 1
    z2 +=1 
    path_points_1 = [(x1, y1, z1 - 1), (x1, y1, z1)]
    path_points_1 = moveHorizontal_overide(x1, x2, y1, z1, path_points_1)
    path_points_1 = moveVertical_overide(x2, y1, y2, z1, path_points_1)
    intersections_1 = set([getPathOccupation(point) for point in path_points_1[1:]])
        
    path_points_2 = [(x1, y1, z1 - 1), (x1, y1, z1)] 
    path_points_2 = moveVertical_overide(x1, y1, y2, z1, path_points_2)
    path_points_2 = moveHorizontal_overide(x1, x2, y2, z1, path_points_2)
    intersections_2 = set([getPathOccupation(point) for point in path_points_2[1:]])

    path_points_1.append((x2, y2, z2 - 1))
    path_points_2.append((x2, y2, z2 - 1))
    if -1 in intersections_1:
        intersections_1.remove(-1)
    if -1 in intersections_2:
        intersections_2.remove(-1)
    
    if len(intersections_2) > len(intersections_1):
        return path_points_1, intersections_1
    else:
        return path_points_2, intersections_2
    

def findPaths(netlist, relay_badness, max_path_length, max_itterations, max_random_moves, num_random_tries):
    """
    Tries to find the paths between al the chips in netlist
    """
    global grid, path_grid, itteration, nets_layd
    shortest_paths = {path_number: [] for path_number in range(len(netlist))}
    path_number = 0
    nets_layd = [False for net_number in range(len(netlist))]
    original_netlist = copy.deepcopy(netlist)
    itteration = -1
    number_of_chips = len(chips)

    while False in nets_layd:
        joined_list = list(itertools.chain.from_iterable(shortest_paths.values()))
        for point in joined_list:
            if isFree(point) or getPathOccupation(point) == -1:
                assert False

        #extra check, remove later
        assert Controle.calculateNumberPathOccupiedPoints(path_grid) == Controle.totalOccupiedPoints(shortest_paths.values()) - 2* len([i for i in nets_layd if i])
        assert Controle.pathGridNormalGridOccupation(grid, path_grid)

        assert -1 not in shortest_paths  # extra check
        itteration += 1
        if itteration == max_itterations:
            break

        # finding a path and its start/end points
        while nets_layd[path_number]:
            path_number += 1
            path_number = path_number % len(netlist)  # to keep cycling through the netlist
        net = netlist[path_number]
        path = []
        start_point, end_point = chips[net[0]], chips[net[1]]
        start, end = netlist[path_number]

        # doing a check, all chips should stay chips
        print "finding a path between %s and %s at the moment I have layed %i paths with at total length of %i and am \
at itteration %i " %(start_point, end_point, len([i for i in nets_layd if i]),calculateWireLenght(shortest_paths.values()) ,itteration)
        for point in chips:
            if getPathOccupation(point) != -2:
                print getPathOccupation(point), point
                assert False


        #trying semi random walk
        for _ in range(num_random_tries):
            if itteration > 100:
                break
            try:
                path = findPossiblePath(start_point, end_point, max_path_length, max_random_moves)
                break
            except (PathLengthError, StuckError):
                setOccupation(start_point)
                setOccupation(end_point)


        if len(path) > 0:  # random walk found a solution
            # print 1, len(path), Controle.calculateNumberOccupiedPoints(grid,chips)
            # smoothends path and corectelly sets occupation. In findPossiblePath points are set to be occupied that
            # the smooth functios removes from the path. So they must be set to be free again
            smoothened_path = Controle.smoothenPath(path)
            for point in smoothened_path[1:-1]:
                if point in path:
                    setPathOccupation(point, path_number)
                else:
                    setOccupation(point, True)
            shortest_paths[path_number] = smoothened_path

            connections_per_chip[start] += 1
            connections_per_chip[end] += 1
            nets_layd[path_number] = True
            setOccupation(start_point)
            setOccupation(end_point)


        else:
            try:
                path, conflicting_paths = AStartAlgoritm(net[0], net[1], max_path_length, relay_badness)
            except:
                path, conflicting_paths = _find_path_overide(start, end)
            try:
                conflicting_paths.remove(path_number)  # cant have conflict with itself
            except:
                pass

            # realaying the conflicting paths
            for conflicting_path_number in conflicting_paths:
                conflicting_path = shortest_paths[conflicting_path_number]
                for point in conflicting_path[1:-1]:  # all points except the endpoints are free again
                    setOccupation(point, True)
                    setPathOccupation(point, -1)
                shortest_paths[conflicting_path_number] = []

            # laying the path itself
            for point in path:
                setOccupation(point)
                setPathOccupation(point, path_number)
            setPathOccupation(start_point, -2)
            setPathOccupation(end_point, -2)

            # set the values in the lists
            shortest_paths[path_number] = path
            connections_per_chip[start] += 1
            connections_per_chip[end] += 1
            nets_layd[path_number] = True
            for conflicting_path in conflicting_paths:
                connections_per_chip[start] += 1
                connections_per_chip[end] += 1
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
            print "programm failed"
            print allowed_intersections, num_intersections
            print net, path
            print shortest_paths
            assert False

    print "The total wire length is %i from %i paths (from a total of %i)and there are %i intersections of which there are %i on the endpoints" % (
        calculateWireLenght(shortest_paths.values()), len([path for path in shortest_paths.values() if len(path) > 0]), len(original_netlist),
        num_intersections, allowed_intersections)
    return shortest_paths


if __name__ == "__main__":
    skips = 0
    X_SIZE = Data.X_SIZE
    Y_SIZE = Data.Y_SIZE_2
    Z_SIZE = Data.Z_SIZE
    chips = Data.chips_2
    path_grid = Grid.createPathGrid()
    grid = Grid.createGrid()
    netlist = Data.netlist_4
    shortest_paths = {path_number: [] for path_number in range(len(netlist))}    # shortest_paths2 = [[(2, 10, 0), (2, 9, 0), (2, 8, 0)], [(12, 3, 0), (11, 3, 0), (10, 3, 0), (9, 3, 0), (9, 4, 0), (8, 4, 0)], [(8, 4, 0), (8, 3, 0), (8, 2, 0), (8, 2, 1), (7, 2, 1), (6, 2, 1), (5, 2, 1), (4, 2, 1), (3, 2, 1), (3, 2, 0)], [(16, 7, 0), (15, 7, 0), (15, 6, 0), (15, 6, 1), (14, 6, 1), (14, 6, 2), (14, 6, 3), (14, 6, 4), (13, 6, 4), (12, 6, 4), (11, 6, 4), (10, 6, 4), (9, 6, 4), (8, 6, 4), (7, 6, 4), (6, 6, 4), (5, 6, 4), (5, 5, 4), (5, 4, 4), (4, 4, 4), (4, 3, 4), (3, 3, 4), (2, 3, 4), (1, 3, 4), (0, 3, 4), (0, 3, 3), (0, 3, 2), (0, 3, 1), (0, 3, 0), (0, 2, 0), (1, 2, 0), (1, 1, 0)], [(3, 2, 0), (3, 3, 0), (3, 3, 1), (3, 3, 2), (3, 4, 2), (3, 4, 3), (3, 4, 4), (3, 5, 4), (4, 5, 4), (4, 6, 4), (4, 6, 3), (4, 7, 3), (5, 7, 3), (6, 7, 3), (7, 7, 3), (8, 7, 3), (9, 7, 3), (10, 7, 3), (10, 7, 2), (11, 7, 2), (12, 7, 2), (12, 7, 1), (13, 7, 1), (13, 7, 0)], [(2, 8, 0), (2, 7, 0), (1, 7, 0), (0, 7, 0), (0, 6, 0), (0, 6, 1), (0, 5, 1), (0, 5, 2), (1, 5, 2), (1, 5, 3), (1, 4, 3), (1, 3, 3), (2, 3, 3), (2, 2, 3), (2, 2, 2), (2, 1, 2), (2, 0, 2), (2, 0, 1), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 0, 0), (6, 0, 0), (6, 1, 0)], [(1, 5, 0), (1, 6, 0), (2, 6, 0), (3, 6, 0), (3, 6, 1), (3, 5, 1), (3, 4, 1), (4, 4, 1), (5, 4, 1), (6, 4, 1), (7, 4, 1), (8, 4, 1), (8, 4, 0)], [(1, 5, 0), (2, 5, 0), (2, 5, 1), (2, 5, 2), (3, 5, 2), (3, 5, 3), (4, 5, 3), (5, 5, 3), (6, 5, 3), (7, 5, 3), (8, 5, 3), (9, 5, 3), (10, 5, 3), (10, 5, 4), (11, 5, 4), (12, 5, 4), (13, 5, 4), (14, 5, 4), (14, 5, 3), (15, 5, 3), (15, 5, 2), (15, 5, 1), (15, 5, 0), (16, 5, 0)], [(12, 3, 0), (12, 4, 0), (11, 4, 0), (10, 4, 0), (10, 4, 1), (10, 4, 2), (9, 4, 2), (8, 4, 2), (7, 4, 2), (7, 5, 2), (7, 5, 1), (7, 6, 1), (7, 7, 1), (7, 8, 1), (6, 8, 1), (6, 8, 0)], [(2, 8, 0), (3, 8, 0), (3, 7, 0), (4, 7, 0), (5, 7, 0), (5, 6, 0), (6, 6, 0), (7, 6, 0), (7, 7, 0), (7, 8, 0), (8, 8, 0), (9, 8, 0)], [(1, 5, 0), (1, 4, 0), (1, 3, 0), (2, 3, 0), (2, 2, 0), (3, 2, 0)], [(6, 1, 0), (7, 1, 0), (7, 2, 0), (7, 3, 0), (7, 4, 0), (8, 4, 0)], [(15, 1, 0), (15, 0, 0), (15, 0, 1), (15, 0, 2), (14, 0, 2), (13, 0, 2), (12, 0, 2), (11, 0, 2), (10, 0, 2), (9, 0, 2), (8, 0, 2), (7, 0, 2), (6, 0, 2), (5, 0, 2), (4, 0, 2), (4, 1, 2), (4, 2, 2), (4, 3, 2), (4, 4, 2), (4, 5, 2), (4, 5, 1), (4, 5, 0)], [(16, 5, 0), (16, 4, 0), (16, 3, 0), (16, 2, 0), (16, 2, 1), (15, 2, 1), (15, 2, 2), (14, 2, 2), (14, 2, 3), (13, 2, 3), (12, 2, 3), (11, 2, 3), (11, 2, 2), (11, 2, 1), (11, 2, 0), (12, 2, 0)], [(4, 5, 0), (5, 5, 0), (6, 5, 0), (7, 5, 0), (8, 5, 0), (8, 4, 0)], [(12, 11, 0), (12, 10, 0), (12, 9, 0), (13, 9, 0), (14, 9, 0), (15, 9, 0), (16, 9, 0), (17, 9, 0), (17, 8, 0), (17, 7, 0), (17, 6, 0), (17, 5, 0), (16, 5, 0)], [(1, 11, 0), (1, 12, 0), (2, 12, 0), (3, 12, 0), (4, 12, 0), (5, 12, 0), (6, 12, 0), (7, 12, 0), (8, 12, 0), (9, 12, 0), (10, 12, 0), (11, 12, 0), (12, 12, 0), (12, 11, 0)], [(1, 1, 0), (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (2, 4, 1), (2, 4, 0), (3, 4, 0), (3, 5, 0), (4, 5, 0)], [(6, 1, 0), (5, 1, 0), (4, 1, 0), (4, 2, 0), (3, 2, 0)], [(1, 9, 0), (1, 9, 1), (1, 9, 2), (1, 9, 3), (2, 9, 3), (3, 9, 3), (4, 9, 3), (4, 9, 2), (5, 9, 2), (6, 9, 2), (7, 9, 2), (8, 9, 2), (9, 9, 2), (9, 8, 2), (10, 8, 2), (11, 8, 2), (11, 8, 1), (11, 8, 0)], [(2, 10, 0), (2, 11, 0), (3, 11, 0), (4, 11, 0), (5, 11, 0), (5, 11, 1), (6, 11, 1), (7, 11, 1), (8, 11, 1), (9, 11, 1), (10, 11, 1), (10, 10, 1), (10, 9, 1), (11, 9, 1), (12, 9, 1), (12, 8, 1), (13, 8, 1), (14, 8, 1), (15, 8, 1), (15, 8, 0)], [(6, 8, 0), (6, 7, 0), (6, 7, 1), (6, 6, 1), (6, 6, 2), (6, 5, 2), (6, 4, 2), (6, 3, 2), (6, 2, 2), (6, 1, 2), (7, 1, 2), (7, 1, 1), (8, 1, 1), (8, 1, 0), (9, 1, 0), (10, 1, 0)], [(9, 10, 0), (8, 10, 0), (7, 10, 0), (7, 10, 1), (6, 10, 1), (5, 10, 1), (4, 10, 1), (3, 10, 1), (3, 9, 1), (3, 9, 2), (2, 9, 2), (2, 8, 2), (2, 8, 3), (2, 7, 3), (2, 6, 3), (2, 5, 3), (2, 4, 3), (2, 4, 2), (2, 3, 2), (2, 3, 1), (2, 2, 1), (2, 1, 1), (2, 1, 0), (1, 1, 0)], [(14, 2, 0), (14, 2, 1), (14, 1, 1), (14, 0, 1), (14, 0, 0), (13, 0, 0), (12, 0, 0), (11, 0, 0), (10, 0, 0), (10, 1, 0)], [(10, 1, 0), (10, 1, 1), (10, 2, 1), (10, 3, 1), (11, 3, 1), (11, 4, 1), (12, 4, 1), (12, 5, 1), (13, 5, 1), (13, 6, 1), (13, 6, 0), (13, 7, 0)], [(16, 7, 0), (16, 6, 0), (16, 5, 0)], [(10, 1, 0), (10, 2, 0), (9, 2, 0), (9, 2, 1), (9, 3, 1), (9, 4, 1), (9, 5, 1), (10, 5, 1), (10, 6, 1), (10, 7, 1), (10, 8, 1), (10, 8, 0), (11, 8, 0)], [(13, 7, 0), (12, 7, 0), (12, 6, 0), (12, 6, 1), (12, 6, 2), (12, 6, 3), (11, 6, 3), (10, 6, 3), (9, 6, 3), (8, 6, 3), (7, 6, 3), (6, 6, 3), (5, 6, 3), (5, 6, 2), (5, 5, 2), (5, 4, 2), (5, 3, 2), (5, 2, 2), (5, 1, 2), (5, 1, 1), (6, 1, 1), (6, 1, 0)], [(2, 8, 0), (2, 8, 1), (2, 9, 1), (2, 10, 1), (2, 11, 1), (2, 12, 1), (3, 12, 1), (4, 12, 1), (5, 12, 1), (6, 12, 1), (7, 12, 1), (8, 12, 1), (9, 12, 1), (10, 12, 1), (11, 12, 1), (11, 11, 1), (12, 11, 1), (12, 11, 0)], [(1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 1, 2), (1, 1, 2), (1, 1, 3), (2, 1, 3), (3, 1, 3), (3, 2, 3), (3, 3, 3), (4, 3, 3), (5, 3, 3), (6, 3, 3), (7, 3, 3), (8, 3, 3), (8, 3, 2), (9, 3, 2), (10, 3, 2), (11, 3, 2), (11, 4, 2), (11, 5, 2), (11, 5, 1), (11, 5, 0)], [(12, 2, 0), (12, 3, 0)], [(15, 1, 0), (14, 1, 0), (13, 1, 0), (12, 1, 0), (11, 1, 0), (10, 1, 0)], [(15, 8, 0), (16, 8, 0), (16, 8, 1), (17, 8, 1), (17, 7, 1), (17, 6, 1), (17, 5, 1), (17, 4, 1), (17, 4, 0), (17, 3, 0), (17, 2, 0), (17, 1, 0), (16, 1, 0), (15, 1, 0)], [(6, 1, 0), (6, 2, 0), (5, 2, 0), (5, 3, 0), (4, 3, 0), (4, 4, 0), (4, 5, 0)], [(15, 8, 0), (14, 8, 0), (13, 8, 0), (13, 7, 0)], [(11, 5, 0), (10, 5, 0), (9, 5, 0), (9, 6, 0), (8, 6, 0), (8, 7, 0), (8, 7, 1), (8, 8, 1), (8, 9, 1), (9, 9, 1), (9, 10, 1), (9, 10, 0)], [(3, 2, 0), (3, 1, 0), (3, 1, 1), (3, 0, 1), (4, 0, 1), (5, 0, 1), (6, 0, 1), (7, 0, 1), (7, 0, 0), (8, 0, 0), (9, 0, 0), (9, 0, 1), (10, 0, 1), (11, 0, 1), (11, 1, 1), (12, 1, 1), (13, 1, 1), (13, 2, 1), (13, 2, 0), (14, 2, 0)], [(4, 5, 0), (4, 6, 0), (4, 6, 1), (4, 7, 1), (5, 7, 1), (5, 7, 2), (6, 7, 2), (7, 7, 2), (7, 6, 2), (8, 6, 2), (9, 6, 2), (10, 6, 2), (11, 6, 2), (11, 6, 1), (11, 7, 1), (11, 7, 0), (11, 8, 0)], [(9, 8, 0), (9, 7, 0), (10, 7, 0), (10, 6, 0), (11, 6, 0), (11, 5, 0)], [(1, 5, 0), (1, 5, 1), (1, 6, 1), (1, 6, 2), (1, 7, 2), (2, 7, 2), (3, 7, 2), (3, 8, 2), (4, 8, 2), (5, 8, 2), (6, 8, 2), (7, 8, 2), (8, 8, 2), (8, 7, 2), (9, 7, 2), (9, 7, 1), (9, 8, 1), (9, 8, 0)], [(6, 8, 0), (6, 9, 0), (6, 10, 0), (6, 11, 0), (7, 11, 0), (8, 11, 0), (9, 11, 0), (10, 11, 0), (11, 11, 0), (12, 11, 0)], [(13, 7, 0), (14, 7, 0), (14, 6, 0), (14, 5, 0), (14, 5, 1), (14, 5, 2), (14, 4, 2), (14, 4, 3), (13, 4, 3), (12, 4, 3), (11, 4, 3), (10, 4, 3), (9, 4, 3), (9, 3, 3), (9, 2, 3), (8, 2, 3), (7, 2, 3), (6, 2, 3), (5, 2, 3), (4, 2, 3), (4, 1, 3), (4, 0, 3), (3, 0, 3), (2, 0, 3), (1, 0, 3), (1, 0, 2), (1, 0, 1), (1, 0, 0), (1, 1, 0)], [(15, 1, 0), (15, 2, 0), (15, 3, 0), (15, 4, 0), (14, 4, 0), (13, 4, 0), (13, 5, 0), (12, 5, 0), (11, 5, 0)], [(1, 11, 0), (1, 11, 1), (1, 11, 2), (1, 11, 3), (1, 10, 3), (2, 10, 3), (3, 10, 3), (4, 10, 3), (5, 10, 3), (5, 9, 3), (5, 8, 3), (6, 8, 3), (7, 8, 3), (8, 8, 3), (9, 8, 3), (10, 8, 3), (11, 8, 3), (11, 7, 3), (12, 7, 3), (13, 7, 3), (13, 6, 3), (13, 5, 3), (12, 5, 3), (12, 5, 2), (12, 4, 2), (12, 3, 2), (12, 3, 1), (12, 3, 0)], [(16, 7, 0), (16, 7, 1), (16, 6, 1), (16, 5, 1), (16, 4, 1), (15, 4, 1), (14, 4, 1), (14, 3, 1), (14, 3, 2), (13, 3, 2), (13, 2, 2), (12, 2, 2), (12, 2, 1), (12, 2, 0)], [(2, 10, 0), (3, 10, 0), (3, 9, 0), (4, 9, 0), (5, 9, 0), (5, 9, 1), (6, 9, 1), (7, 9, 1), (7, 9, 0), (8, 9, 0), (9, 9, 0), (9, 8, 0)], [(11, 8, 0), (11, 9, 0), (10, 9, 0), (10, 10, 0), (9, 10, 0)], [(14, 2, 0), (14, 3, 0), (13, 3, 0), (13, 3, 1), (13, 4, 1), (13, 4, 2), (13, 5, 2), (13, 6, 2), (13, 7, 2), (13, 8, 2), (12, 8, 2), (12, 9, 2), (11, 9, 2), (10, 9, 2), (10, 10, 2), (9, 10, 2), (8, 10, 2), (7, 10, 2), (6, 10, 2), (5, 10, 2), (4, 10, 2), (3, 10, 2), (2, 10, 2), (1, 10, 2), (1, 10, 1), (1, 10, 0), (1, 9, 0)], [(1, 5, 0), (0, 5, 0), (0, 4, 0), (0, 4, 1), (0, 4, 2), (1, 4, 2), (1, 3, 2), (1, 2, 2), (1, 2, 3), (1, 2, 4), (2, 2, 4), (3, 2, 4), (4, 2, 4), (5, 2, 4), (5, 1, 4), (5, 1, 3), (6, 1, 3), (7, 1, 3), (8, 1, 3), (8, 1, 2), (9, 1, 2), (10, 1, 2), (11, 1, 2), (12, 1, 2), (13, 1, 2), (14, 1, 2), (15, 1, 2), (15, 1, 1), (15, 1, 0)], [(6, 8, 0), (5, 8, 0), (4, 8, 0), (4, 8, 1), (3, 8, 1), (3, 7, 1), (2, 7, 1), (1, 7, 1), (1, 8, 1), (1, 8, 0), (1, 9, 0)]]
    

    for i in range(0):
##        random.seed("piza")
        skips = 0
        netlist = Data.netlist_4
        netlist = Grid.sortDistance(netlist)
        connections_per_chip = netlist_checker.connectionsPerChip(netlist, chips)

        path_grid = Grid.createPathGrid()
        grid = Grid.createGrid()
        neighbour_grid = createNeighbourGrid()
        # assert False
        relay_list = [0 for i in netlist]
        relay_badness, max_path_length, max_itterations, max_random_moves, num_random_tries = 15, 60, 3000, 10, 3
        shortest_paths = findPaths(netlist, relay_badness, max_path_length, max_itterations, max_random_moves, num_random_tries)
        print shortest_paths
        print relay_list
        print skips


        aantal_paden_gelegd = len([path for path in shortest_paths.values() if len(path) > 0])
        totaal_paden = len(netlist)
        # safe output
        if aantal_paden_gelegd == totaal_paden:
            Controle.safe(netlist, shortest_paths, relay_list)
    layer = 0
    Visualization.runVisualization(shortest_paths.values(), layer)
        # Visualization.run3DVisualisation(shortest_paths.values(), "joris is cool")h
