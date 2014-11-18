__author__ = 'Marcella Wijngaarden'
import numpy as np
import random
import data
import Visualization
import grid
import itertools
import operator

netlist = data.netlist
chips = data.chips

class PathLengthError(Exception):
    def __init__(self):
        pass

def sortDistance(netlist):
    """
    For a given netlist calculates the distances between the given to be connected chips. Then returns
    the netlist sorted by distance (shortes distance first).
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
                if direction == 1 and dimension == 2:
                    continue
            #if bottom you cant go down
            elif point[2] == 0:
                if direction == -1 and dimension == 2:
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
                if not isFree((x, y, z)):
                    occupied_points.append((x, y, z))

    # print len(occupied_points), len([1 for  z in grid for y in z for x in y if not x])
    return occupied_points

def checkDirection(neighbour, current_point, end):
    """
    Returns True if the neighbour point is in the direction of the endpoint
    """

    for i in range(3):
        delta = abs(end[i] - current_point[i])
        if abs(end[i] - neighbour[i]) < delta and delta >= 0:
            return True, i

    return False, None

def checkDimension(neighbour, current_point):
    """
    Returns True if the neighbour point is in the direction of the endpoint
    """
    for i in range(3):
        delta = abs(neighbour[i] - current_point[i])
        if delta > 0:
            return i

def areNeighbours(point1, point2):
    distance = 0
    for dimension in range(3):
        distance += (point1[dimension] - point2[dimension])**2
    distance = distance**.5
#    print point1, point2, distance
    return distance == 1

def smoothenPath(path):
    for i in range(len(path)):
        for j in range(i+2, len(path)):
            if areNeighbours(path[i], path[j]):
                return smoothenPath(path[:i+1] + path[j:])  # plus 1 to include endpoint

    return path

# def makePathGrid(shortest_paths):
#
#
#
# def relayPaths(shortest_paths):
#
#     grid_located = makePathGrid(shortest_paths)


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
        j = i + 1
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

#def relayPaths(shortest_paths):


def findPath(start, end, grid2):
    global grid
    grid = grid2

    x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(start, end)

    start = (x_start, y_start, z_start)
    end = (x_end, y_end, z_end)
    setOccupation(end, True)

    directions = []
    all_states = []
    path_points = [start]
    path_found = False
    current_point = start
    last_point = start
    print 'finding path between = ', start, ' and ',  end
    dont_go_to = (-1, -1, -1)
    counter = 0
    while not path_found:
#        print 'path = ', path_points
        counter += 1
        if counter == 150: # If the loop is repeated a lot, this means the path is stuck, the other paths are relayed
            print 'stuck', len(shortest_paths)
            return 'Error'


        free_neighbours = freeNeighbour(current_point)
        same_direction = False
        in_direction = False
        neighbours_in_direction = []
        neighbours_other_direction = []

        for neighbour in free_neighbours:
            direction = checkDirection(neighbour, current_point, end)
            if direction[0] and neighbour != dont_go_to: #neighbour not in all_states:
                neighbours_in_direction.append([neighbour, direction[1]])
            elif direction[0] is False and neighbour != dont_go_to: #and neighbour not in all_states:
                neighbours_other_direction.append([neighbour, direction[1]])
            else:
                continue

        for neighbour in neighbours_in_direction:
            if len(directions) == 0 or neighbour[1] == directions[-1]:
                path_points.append(neighbour[0])
                all_states.append(neighbour[0])
                directions.append(neighbour[1])
                setOccupation(neighbour[0], False)
                current_point = neighbour[0]
                same_direction = True
                in_direction = True
#                print 'print go to neighbour, next'
                break
            else:
#                print 'try next neighbour'
                continue

        if not same_direction and len(neighbours_in_direction) > 0:
            step = False
            for neighbour in neighbours_in_direction:
#                print 'list length same direction= ', len(neighbours_in_direction)
                if neighbour[1] < 2:
                    path_points.append(neighbour[0])
                    all_states.append(neighbour[0])
                    directions.append(neighbour[1])
                    setOccupation(neighbour[0], False)
                    current_point = neighbour[0]
                    in_direction = True
                    step = True
                    break
                else:
                    continue

            if not step:
                for neighbour in neighbours_in_direction:
                    if neighbour[1] == 2:
                        path_points.append(neighbour[0])
                        all_states.append(neighbour[0])
                        directions.append(neighbour[1])
                        setOccupation(neighbour[0], False)
                        current_point = neighbour[0]
                        in_direction = True

        if not in_direction and len(neighbours_other_direction) > 0:
            step = False
            i = random.randrange(len(neighbours_other_direction))
            for neighbour in neighbours_other_direction:
#                print 'list length = ', len(neighbours_other_direction)
                if neighbour[1] < 2:
                    path_points.append(neighbour[0])
                    all_states.append(neighbour[0])
                    directions.append(neighbour[1])
                    setOccupation(neighbour[0], False)
                    current_point = neighbour[0]
                    in_direction = True
                    step = True
                    break
                else:
                    continue

            if not step:
                for neighbour in neighbours_other_direction:
                    if neighbour[1] == 2:
                        path_points.append(neighbour[0])
                        all_states.append(neighbour[0])
                        directions.append(neighbour[1])
                        setOccupation(neighbour[0], False)
                        current_point = neighbour[0]
                        in_direction = True


        if len(free_neighbours) == 0 or (len(free_neighbours) == 1 and free_neighbours[0] == dont_go_to):
            if len(path_points) == 1:
                print 'no possible connections'
                return path_points, grid
            print 'no possible neighbours'
            dont_go_to = path_points[-1]
            setOccupation(path_points[-1], True)
            del path_points[-1]

            current_point = path_points[-1]

        print current_point

        if current_point == end:
#            path_points = smoothenPath(path_points)
#            print 'path found :', path_points
            path_points_smoothed = superSmoothPath(path_points)
            path_found = True
            if len(path_points) != len(path_points_smoothed):
                print 'path found before:', len(path_points), path_points
                print 'path found after :', len(path_points_smoothed), path_points_smoothed
            return path_points_smoothed, grid


if __name__ == "__main__":
    shortest_paths = []
    grid = grid.createGrid()
    netlist = sortDistance(netlist)
    print len(netlist)
    print netlist[16]
#    netlist = [netlist[0], netlist[1], netlist[2], netlist[3], netlist[4], netlist[5]]
    netlist = [netlist[i] for i in range(35)]
#    netlist = [netlist[6]]
    for net in netlist:
        path = []
        start, end = chips[net[0]], chips[net[1]]
        print "finding a path betweeen: ", net[0], net[1]
        original_value_start, original_value_end = isFree(start), isFree(end)

        path, grid = findPath(start, end, grid) #findPossiblePath(start, end, grid)
        shortest_paths.append(path)

    print "The number of complete paths should be %i, the actual number of complete paths is %i " % (len(netlist), len(shortest_paths))
#    print "The total wire length is %i and there are %i intersections of which there are %i on the chips" % (
 #       calculateWireLenght(shortest_paths),
  #      checkIntersections(shortest_paths), doubleStartEndPoints(netlist))
    layer = 0
    Visualization.runVisualization(shortest_paths, layer)

