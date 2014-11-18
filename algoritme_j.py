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
    return (0 < point[0] < X_SIZE) and (0 < point[1] < Y_SIZE) and (0 < point[2] <Z_SIZE)


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



def findPossiblePath(point1, point2, max_path_length = 80):
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
            # print "found: ", path_points, "occupied", findOccupiedPoints()
            return path_points, grid


# noinspection PyUnreachableCode
def AStartAlgoritm(point1, point2, maxdept = 60):


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


    a_star_grid = np.ndarray(shape=(X_SIZE, Y_SIZE, Z_SIZE), dtype=list)
    #grid is filled with list [number, set with conflicts]
    a_star_grid.fill([maxdept,range(maxdept)])  # try to improve so have to start with global worse case senario

    temp_current_points = [point1]
    setAStarValue(point1, [0,[]])
    setOccupation(point2, True)
    setOccupation(point1, True)
    setPathOccupation(point1, -1)
    setPathOccupation(point2, -1)

    for itteration in range(maxdept):
        current_points = set(temp_current_points)
        # print "going down deeper, itteration %i, we have %i points to move" %(itteration, len(current_points))
        current_points = set(temp_current_points)
        temp_current_points = []

        for point in current_points:
            neighbours = findNeighbours(point)
            value = getAStarValue(point)
            value[0] += 1
            # print value[0]
            # print Controle.getAvrgValueAStarDistance(a_star_grid)
            # print value
            for neighbour in neighbours:
                AStar_value = copy.deepcopy(value)
                # print AStar_value, value
                current_value_neighbour = getAStarValue(neighbour)

                if not isFree(neighbour):
                    # print "not free", AStar_value, value
                    intersectiong_path = getPathOccupation(neighbour)
                    if intersectiong_path == -1:
                        if neighbour == point2:
                            assert False
                        else:
                            pass  # if a point is not free but intersection is -1 then it is a chip
                    AStar_value[1].append(intersectiong_path)
                    # print "after not free", AStar_value, value
                    # assert False
                if len(set(AStar_value[1])) < len(set(current_value_neighbour[1])):
                    setAStarValue(neighbour, AStar_value)
                    temp_current_points.append(neighbour)
                elif len(set(AStar_value[1])) == len(set(current_value_neighbour[1])) and AStar_value[0] < current_value_neighbour[0]:
                    setAStarValue(neighbour, AStar_value)
                    temp_current_points.append(neighbour)
                # print getAStarValue(neighbour)
            # print Controle.getAvrgValueAStarDistance(a_star_grid)
            # assert False

    final_astar_path = [point2]
    current_point = point2
    best_neigbour = current_point
    while current_point != point1:
        value_best_neigbour = getAStarValue(current_point)  # at the start the best position is the starting position
        # print "finding my way back from %s which has a value of %s" %(str(current_point), str(value_best_neigbour))

        for neighbour in findNeighbours(current_point):
            value_neighbour = getAStarValue(neighbour)
            if len(set(value_neighbour[1])) < len(set(value_best_neigbour[1])):
                best_neigbour = neighbour
            elif len(set(value_neighbour[1])) == len(set(value_best_neigbour[1])) and value_neighbour[0] < value_best_neigbour[0]:
                best_neigbour = neighbour

        if best_neigbour == current_point:  # check to see if a best neighbour is found
            print current_point, value_best_neigbour
            print point1, point2
            print [len(getAStarValue(i)[1]) for i in  findNeighbours(current_point)]
            raise AstarError
        else:
            final_astar_path.append(best_neigbour)
            current_point = best_neigbour

    conflicting_paths = []
    for point in final_astar_path:
        conflicting_paths.append(getPathOccupation(point))
    conflicting_paths = set(conflicting_paths)
    if -1 in conflicting_paths:
        conflicting_paths.remove(-1)

    return final_astar_path, conflicting_paths


def findPaths(netlist, max_tries = 10):
    """
    Tries to find the paths between al the chips in netlist
    """
    shortest_paths = {path_number: [] for path_number in range(len(netlist))}
    path_number = 0
    nets_layd = [False for net_number in range(len(netlist))]
    original_netlist = copy.deepcopy(netlist)
    i = 0
    path_tries = [0 for _ in netlist]
    while False in nets_layd:
        assert -1 not in shortest_paths
        i += 1
        if i == 1000:
            print path_tries
            break
        while nets_layd[path_number]:
            path_number += 1
            path_number = path_number % len(netlist)  # to keep cycling through the netlist
        net = netlist[path_number]
        path_tries[path_number] += 1
        path = []
        try:
            start, end = chips[net[0]], chips[net[1]]  # should not give error but I had trouble with this once.
        except:
            print chips, net
            assert False
        # print "finding a path betweeen: ", chips[net[0]], chips[net[1]]
        original_value_start, original_value_end = isFree(start), isFree(end)

        print "finding a path between %s and %s" %(start, end)
        for _ in range(max_tries):
            try:
                path, grid = findPossiblePath(start, end)
                break
            except (PathLengthError, StuckError):
                setOccupation(start, original_value_start)
                setOccupation(end, original_value_end)

        if len(path) > 0:
            #smoothends path and corectelly sets occupation
            smoothened_path = Controle.smoothenPath(path)
            for point in path:
                if point not in smoothened_path:
                    setOccupation(point, True)
                else:
                    setPathOccupation(point, path_number)
            shortest_paths[path_number] = smoothened_path
            nets_layd[path_number] = True

        else:
            print "path not found, trying Astar algorithm"
            path, conflicting_paths = AStartAlgoritm(start, end)
            try:
                conflicting_paths.remove(path_number)
            except:
                pass
            for conflicting_path_number in conflicting_paths:
                conflicting_path = shortest_paths[conflicting_path_number]
                for point in conflicting_path:
                    setOccupation(point, True)
                    setPathOccupation(point, -1)
                shortest_paths[conflicting_path_number] = []

            for point in path:
                setOccupation(point)
                setPathOccupation(point, path_number)

            shortest_paths[path_number] = path
            nets_layd[path_number] = True
            for conflicting_path in conflicting_paths:
                nets_layd[conflicting_path] = False
            print "path found but paths %s will have to be refound" %(conflicting_paths)


    print "The total wire length is %i from %i paths (from a total of %i)and there are %i intersections of which there are %i on the endpoints" % (
        calculateWireLenght(shortest_paths.values()), len([path for path in shortest_paths.values() if len(path) > 0]), len(original_netlist),
        checkIntsections(shortest_paths.values()), doubleStartEndPoints(original_netlist))
    print shortest_paths
    return shortest_paths


if __name__ == "__main__":

    X_SIZE = Data.X_SIZE
    Y_SIZE = Data.Y_SIZE
    Z_SIZE = Data.Z_SIZE
    netlist = Data.netlist
    chips = Data.chips
    path_grid = Grid.createPathGrid()
    grid = Grid.createGrid()

    print 'finding paths'
    print netlist
    shortest_paths = findPaths(netlist)
    print shortest_paths
    # print Controle.connectionsPerChip(netlist)
    # print Controle.doubleConnections(netlist)
    # print min([len(i) for i in shortest_paths.values()])
    # print max([len(i) for i in shortest_paths.values()])
    layer = 3
    Visualization.runVisualization(shortest_paths.values(), layer)