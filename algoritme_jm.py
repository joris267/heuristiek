import numpy as np
import random
import data
import Visualization
import grid
import itertools

netlist = data.netlist
chips = data.chips

class PathLengthError(Exception):
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


def checkIntersections(path_list):
    """
    Checks if there are intersections in the path.
    Returns the number of intersections in the path
    """
    som = 0
    joined_list = [hash(i) for i in list(itertools.chain.from_iterable(path_list))]  # lelijk
    occurrences = np.bincount(joined_list)
    for i in occurrences:
        if i > 1:
            som += i
    return som

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
        for i in chip_to_occurrences.values():
            if i > 1:
                som += i
    return som

def isFree(point):
    """
    For a given point (x,y,z) returns True if free, else False
    """
    global grid
    for i in point:
        if i < 0:
            return False
    try:
        value = grid[point[0]][point[1]][point[2]]
      #  print value
    except:
        print "point ", point, "lies outside of grid"
        value = False
    return value

def setOccupation(point, occupation=False):
    """
    For a given point changes it's value in the grid to the given occupation.
    Returns nothing.
    """
    grid[point[0]][point[1]][point[2]] = occupation

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

    endpoint = (x, y_start + i, layer)
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

            #if on top layer, you cant go up
            if point[2] == 7:
                if direction == 1 and dimension == 3:
                    continue
            #if bottom you cant go down
            elif point[2] == 0:
                if direction == -1 and dimension == 3:
                    continue

            list_point = list(point)
            list_point[dimension] += direction
            neighbour = tuple(list_point)
            if isFree(neighbour):
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



def findPossiblePath(start, end, grid2):
    global grid
    grid = grid2

    x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(start, end)
    occupied_points = len(findOccupiedPoints())

    start = (x_start, y_start, z_start)
    end = (x_end, y_end, z_end)
    setOccupation(end, True)

    path_points = [start]
    path_found = False
    current_point = start
    print 'point = ', current_point

    while not path_found:
        if len(path_points) > 80:
            print "path too long"
            for point in path_points:
                setOccupation(point, True)
            #return findPossiblePath(start, end, grid)
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
                path_points, current_point = moveUpDPown(current_point[0], current_point[1], current_point[2], z_end, path_points)

        # print "path: ", path_points  # len([1 for  z in grid for y in z for x in y if not x])
        # print findOccupiedPoints()
        # print occupied_points, len(path_points)
        # print len(findOccupiedPoints())
#        assert occupied_points + len(path_points) == len(findOccupiedPoints())
        if last_point == current_point:
 #           findPossiblePath(start, end, grid, path_points)
            free_neighbours = freeNeighbour(current_point)
            if len(free_neighbours) == 0:
                for i in range(1, len(path_points)):
                    setOccupation(path_points[i], True)
                del path_points
                path_points = [start]
                print "stuck: try again"
#                return findPossiblePath(start, end, grid)
                #return path_points, grid
            else:
                current_point = random.choice(free_neighbours)
                path_points.append(current_point)
                setOccupation(current_point)

#        assert occupied_points + len(path_points) == len(findOccupiedPoints())

        if current_point == end:
            print "found: ", path_points, "occupied", findOccupiedPoints()
            return path_points, grid


if __name__ == "__main__":
    shortest_paths = []
    grid = grid.createGrid()
#    netlist = [netlist[0], netlist[1], netlist[2], netlist[3], netlist[4], netlist[5]]
<<<<<<< HEAD
    netlist = [netlist[i] for i in range(35)]
#    netlist = [netlist[6]]
=======
    netlist = [netlist[i] for i in range(11)]
>>>>>>> origin/master
    for net in netlist:
        path = []
        start, end = chips[net[0]], chips[net[1]]
        print "finding a path betweeen: ", chips[net[0]], chips[net[1]]
        original_value_start, original_value_end = isFree(start), isFree(end)
        while len(path) < 1:
            try:
                path, grid = findPossiblePath(start, end, grid)
                break
            except PathLengthError:
                break
                setOccupation(start, original_value_start)
                setOccupation(end, original_value_end)
                print "Occupation is changed"
                print 'PathLengthError'

        shortest_paths.append(path)


    print "The number of complete paths should be %i, the actual number of complete paths is %i " % (len(netlist), len(shortest_paths))
 #   print "The total wire length is %i and there are %i intersections of which there are %i on the chips" % (
  #      calculateWireLenght(shortest_paths),
   #     checkIntersections(shortest_paths), doubleStartEndPoints(netlist))
    print shortest_paths
    layer = 3
    Visualization.runVisualization(shortest_paths, layer)
