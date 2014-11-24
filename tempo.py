import numpy as np
import random
import data
import Visualization
import grid
import itertools
import operator
import copy
import breadth_first_algoritme

path_grid = breadth_first_algoritme.path_grid #grid.createPathGrid()
grid = breadth_first_algoritme.grid
#netlist = sortDistance(netlist)
X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
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

def inGrid(point):
    return (0 <= point[0] < X_SIZE) and (0 <= point[1] < Y_SIZE ) and (0 <= point[2] < Z_SIZE)

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
        #print "point ", point, "lies outside of grid"
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
    #print 'begin'
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

#def reconstructPaths(shortest_paths):

def findMinimalIntersectingPath(start, end):
    """
    Finds a path between two points that is the shortest possible for the smallest amount of intersections: A* method
    """
    global path_grid

    def findHeuristic(neighbour, end):
        value = 0
        for i in range(3):
            delta = abs(end[i] - neighbour[i])
            value += delta
        return value



def AStartAlgoritm(point1, point2, maxdept=60):

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
    a_star_grid.fill([maxdept, range(maxdept)])  # try to improve so have to start with global worse case scenario

    temp_current_points = [point1]
    setAStarValue(point1, [0, []])
    setOccupation(point2, True)
    setOccupation(point1, True)
    setPathOccupation(point1, -1)
    setPathOccupation(point2, -1)

    for iteration in range(maxdept):
        #current_points = set(temp_current_points)
        # print "going down deeper, iteration %i, we have %i points to move" %(iteration, len(current_points))
        current_points = set(temp_current_points)
        temp_current_points = []

        for point in current_points:
            neighbours = findNeighbours(point)
            try:
                value = getAStarValue(point)
            except:
                print point
                assert False

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
                    intersectiong_path = breadth_first_algoritme.getPathOccupation(neighbour)
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
    best_neighbour = current_point
    while current_point != point1:
        value_best_neighbour = getAStarValue(current_point)  # at the start the best position is the starting position
        # print "finding my way back from %s which has a value of %s" %(str(current_point), str(value_best_neigbour))

        for neighbour in findNeighbours(current_point):
            value_neighbour = getAStarValue(neighbour)
            if len(set(value_neighbour[1])) < len(set(value_best_neighbour[1])):
                best_neighbour = neighbour
            elif len(set(value_neighbour[1])) == len(set(value_best_neighbour[1])) and value_neighbour[0] < value_best_neighbour[0]:
                best_neighbour = neighbour

        if best_neighbour == current_point:  # check to see if a best neighbour is found
            print current_point, value_best_neighbour
            print point1, point2
            print [len(getAStarValue(i)[1]) for i in findNeighbours(current_point)]
            raise AstarError
        else:
            final_astar_path.append(best_neighbour)
            current_point = best_neighbour

    conflicting_paths = []
    for point in final_astar_path:
        conflicting_paths.append(getPathOccupation(point))
    conflicting_paths = set(conflicting_paths)
    if -1 in conflicting_paths:
        conflicting_paths.remove(-1)

    return final_astar_path, conflicting_paths


def findPath(start, end, grid2):
    global grid
    grid = grid2

    setOccupation(end, True)

    directions = []
    all_states = []
    path_points = [start]
    path_found = False
    current_point = start
    last_point = start
    #print 'Finding path between = ', start, ' and ',  end
    dont_go_to = (-1, -1, -1)
    counter = 0
    while not path_found:
#        print 'path = ', path_points
        counter += 1
        if counter == 190: # If the loop is repeated a lot, this means the path is stuck, the other paths are reconstructed
#            print 'stuck', len(shortest_paths), (start, end)
            return [], grid


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
                return [], grid
            #print 'no possible neighbours'
            dont_go_to = path_points[-1]
            setOccupation(path_points[-1], True)
            del path_points[-1]

            current_point = path_points[-1]

        #print current_point

        if current_point == end:
#            path_points = smoothenPath(path_points)
#            print 'path found :', path_points
            path_points_smoothed = superSmoothPath(path_points)
            path_found = True
            #if len(path_points) != len(path_points_smoothed):
                #print 'path found before:', len(path_points), path_points
                #print 'path found after :', len(path_points_smoothed), path_points_smoothed
            return path_points_smoothed, grid

def startAlgorithms():
    global grid
    stuck_paths = []
    stuck = 0
    path_number = 0
    shortest_paths_dict = {}
    stuck_paths_dict = {}

    for net in netlist:
        start, end = chips[net[0]], chips[net[1]]
        print "finding a path betweeen: ", net[0], net[1]
        original_value_start, original_value_end = isFree(start), isFree(end)
        x_start, x_end, y_start, y_end, z_start, z_end = calculateEndStart(start, end)

        start = (x_start, y_start, z_start)
        end = (x_end, y_end, z_end)

        path, grid = findPath(start, end, grid)
        if len(path) == 0:
            stuck += 1
            stuck_paths.append((start, end))
            stuck_paths_dict[path_number] = path
        else:
            for point in path:
                setPathOccupation(point, path_number)
            shortest_paths_dict[path_number] = path
            shortest_paths.append(path)
        path_number += 1

    temp_new_paths = []
    for path in stuck_paths:
        new_path, new_stuck_paths = AStartAlgoritm(path[0], path[1])[0], AStartAlgoritm(path[0], path[1])[1]
       # print "new_stuck_paths = ", new_stuck_paths

        if len(new_stuck_paths) == 0:
            if new_path[0] == start and new_path[-1] == end:
                shortest_paths.append(new_path)
                stuck_paths.remove(path)
            else:
                continue
        else:
            temp_new_paths.append(new_path)
            for group in range(len(new_stuck_paths)):
                temp_new_paths.append(group)
            #print "temp_new_paths = ", temp_new_paths

    return shortest_paths, stuck_paths, temp_new_paths

if __name__ == "__main__":
    shortest_paths = []
    path_grid = grid.createPathGrid()
    grid = grid.createGrid()
    netlist = sortDistance(netlist)
    X_SIZE = data.X_SIZE
    Y_SIZE = data.Y_SIZE
    Z_SIZE = data.Z_SIZE
#    netlist = [netlist[0], netlist[1], netlist[2], netlist[3], netlist[4], netlist[5]]
    netlist = [netlist[i] for i in range(50)]
#    netlist = [netlist[6]]
    shortest_paths, stuck_paths, new_stuck_paths = startAlgorithms()[0], startAlgorithms()[1], startAlgorithms()[2]

    print len(shortest_paths), len(stuck_paths), len(new_stuck_paths)
    print "Total length netlist = ", len(netlist)
#    print "The number of complete paths should be %i, the actual number of complete paths is %i " % (len(netlist), len(shortest_paths)-stuck)
#    print "Number of stuck nets : ", stuck, ' stuck paths : ', stuck_paths
#    print "The total wire length is %i and there are %i intersections of which there are %i on the chips" % (
 #       calculateWireLenght(shortest_paths),
  #      checkIntersections(shortest_paths), doubleStartEndPoints(netlist))
    layer = 0
    Visualization.runVisualization(shortest_paths, layer)
