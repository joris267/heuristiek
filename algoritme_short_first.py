__author__ = 'Rick'

import data
import grid_copy as grid
import Visualization
import random
import weights
import time

print "Imported"

WEST = 0
NORTH = 1
EAST = 2
SOUTH = 3
UP = 4
DOWN = 5

directions = [WEST, NORTH, EAST, SOUTH, UP, DOWN]

chips = data.chips
netlist = data.netlist
print "Netlist size:", len(netlist)

data_grid = grid.grid

nets_unsorted = []  # List with start and end points of lines
final_paths = {}
total_no_of_paths = len(netlist)
not_layed_paths = set(range(len(netlist)))

index_path_dict = {}

for k, path in enumerate(netlist):  # Making routes_unsorted
    chip_start = path[0]
    chip_end = path[1]
    nets_unsorted.append((chips[chip_start], chips[chip_end]))
    final_paths[k] = []


def minPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1]) + abs(points[0][2] - points[1][2])


def areNeighbours(point1, point2):
    distance = 0
    for dimension in range(3):  # For x, y and z
        distance += (point1[dimension] - point2[dimension])**2
    distance **= .5
    return distance == 1


def superSmoothPath(path):

    old_path = path
    i = 0
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

    return path


def checkConnections(first_point, second_point, path):

    current_length = len(path)
    #check if the points are on one line
    delta_x = abs(max(first_point[0], second_point[0]) - min(first_point[0], second_point[0]))
    delta_y = abs(max(first_point[1], second_point[1]) - min(first_point[1], second_point[1]))
    delta_z = abs(max(first_point[2], second_point[2]) - min(first_point[2], second_point[2]))

    # delta_x = abs(first_point[0] - second_point[0])
    # delta_y = abs(first_point[1] - second_point[1])
    # delta_z = abs(first_point[2] - second_point[2])

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
                if not grid.isOccupied(check_point) or check_point in path:
                    track.append(check_point)
                    # print 'track = ', track
                    if check_point == second_point and len(track) < current_length:
                        if track != path:
                            # print 'track returned'
                            return track
                        else:
                            break
                    else:
                        continue
                else:
                    return None
    return None


def smoothPath(path):
    for i in range(len(path)):
        for j in range(i+2, len(path)):
            if areNeighbours(path[i], path[j]):
                return smoothPath(path[:i+1] + path[j:])  # plus 1 to include endpoint
    return path


def getNextPoint(point, direction):
    """
    Returns the next point given the direction
    """
    if direction == WEST:
        return point[0] - 1, point[1], point[2]
    if direction == NORTH:
        return point[0], point[1] - 1, point[2]
    if direction == EAST:
        return point[0] + 1, point[1], point[2]
    if direction == SOUTH:
        return point[0], point[1] + 1, point[2]
    if direction == UP:
        return point[0], point[1], point[2] + 1
    if direction == DOWN:
        return point[0], point[1], point[2] - 1


def getWeight(path, point2, next_point, path_occupation_set):
    """
    Calculates the chance that next_point should be accepted.
    A desirable next_point will have a bigger chance than a less desirable.
    Chances bigger than 1 will also be accepted
    """
    weight = 1
    if grid.notInGrid(next_point):          # If next_point is not inside of the grid
        return 0
    if next_point in chips:                 # If next_point if occupied by a chip
        return 0
    if grid.isOccupied(next_point):# and grid.getPointOccupation(next_point) not in path_occupation_set:  # If next_point is occupied
        weight *= weights.POSITION_OCCUPIED
    if next_point in path:                  # If next_point is already in the path
        weight *= weights.PASS_THROUGH_SELF
    if minPathLength((next_point, point2)) < minPathLength((path[-1], point2)):  # next_point brings it closer to point2
        weight *= weights.CLOSER_TO_DEST
    else:                                   # next_point goes away from point2
        weight *= weights.AWAY_FROM_DEST

    return weight


def aStarPathFinder(point1, point2):
    """
    point1: the start of the path
    point2: the end of the path
    returns a path using the A* method combined with simulated annealing
    """
    path = [point1]
    done = False
    tries = 0
    path_occupation_set = set()
    while not done:
        tries += 1
        if tries > weights.MAX_TRIES:
            return []
        last_point = path[-1]
        next_point = getNextPoint(last_point, random.choice(directions))
        if next_point == point2:
            # If the next_point is the end point
            path.append(next_point)
            done = True
            continue
        if random.random() <= getWeight(path, point2, next_point, path_occupation_set):
            # Accept next point
            occupation__value = grid.getPointOccupation(next_point)
            if occupation__value != -1:
                path_occupation_set.add(occupation__value)
            path.append(next_point)
            continue  # Continue, find next point

    return superSmoothPath(path)


def main():
    netlist_sorted = sorted(nets_unsorted, key=minPathLength)  # Sort nets_unsorted by minimum length

    iteration = 0
    fail_combo = 0
    fail_combo_list = []
    while not_layed_paths != set([]):
        iteration += 1
        if iteration % 100 == 0:
            print "Iteration:", iteration
            print "Paths layed:", len(netlist) - len(not_layed_paths)

        if iteration > weights.MAX_ITERATIONS:
            print "Max fail combo:", max(fail_combo_list)
            break

        path_id = random.choice(list(not_layed_paths))
        net = netlist_sorted[path_id]
        #print "Finding path for id:", path_id, "net:", net
        path = aStarPathFinder(net[0], net[1])
        if path != []:
            #print "Fail combo:", fail_combo
            fail_combo_list.append(fail_combo)
            fail_combo = 0
            not_layed_paths.remove(path_id)
            conflicts = grid.getOccupation(path)
            #print "No of conflicts of current path:", len(conflicts)
            for conflict in conflicts:
                grid.clearOccupation(final_paths[conflict])     #
                final_paths[conflict] = []                      # The conflicting path is erased
                not_layed_paths.add(conflict)                   #
            grid.setOccupation(path, path_id)
            final_paths[path_id] = path

        else:  # If path takes too long to find in aStarPathFinder
            #print "Takes too long to find path, try other one"
            fail_combo += 1
            continue
    print "Iteration:", iteration
    print "Paths layed:", len(netlist) - len(not_layed_paths)
    return final_paths.values()


def runMain():
    time_start = time.clock()
    path_list = main()
    time_end = time.clock()
    path_length = 0
    for index, path in enumerate(path_list):
        path_list[index] = superSmoothPath(path)
        path_length += len(path) - 1
    print "Path length:", path_length
    print "Calculated in:", int(time_end - time_start), "seconds"
    Visualization.runVisualization(path_list)
    Visualization.run3DVisualisation(path_list, 0)


def runTest():
    start = time.clock()
    #path = aStarPathFinder((1, 1, 0), (15, 8, 0))
    path = [(1, 1, 0), (1, 2, 0), (1, 3, 0), (1, 3, 1), (1, 4, 1), (1, 5, 1), (2, 5, 1), (3, 5, 1), (3, 5, 0), (3, 6, 0), (4, 6, 0), (5, 6, 0), (5, 7, 0), (5, 8, 0), (5, 8, 1), (4, 8, 1), (4, 7, 1), (4, 7, 2), (5, 7, 2), (6, 7, 2), (7, 7, 2), (7, 7, 1), (7, 8, 1), (8, 8, 1), (8, 9, 1), (8, 9, 0), (9, 9, 0), (10, 9, 0), (10, 8, 0), (10, 7, 0), (10, 6, 0), (11, 6, 0), (12, 6, 0), (12, 7, 0), (12, 8, 0), (13, 8, 0), (14, 8, 0), (15, 8, 0)]
    end = time.clock()
    print "Path calculate time", end - start
    print "Path length: ", len(path)

    Visualization.run3DVisualisation([path], 0)
    start = time.clock()
    smoother_path = smoothPath(path)
    end = time.clock()
    print "Smooth in:", end - start
    Visualization.run3DVisualisation([smoother_path], 0)

    ####
    #### Path that needs smoohting:
    #### [(1, 1, 0), (1, 2, 0), (1, 3, 0), (1, 3, 1), (1, 4, 1), (1, 5, 1), (2, 5, 1), (3, 5, 1), (3, 5, 0), (3, 6, 0), (4, 6, 0), (5, 6, 0), (5, 7, 0), (5, 8, 0), (5, 8, 1), (4, 8, 1), (4, 7, 1), (4, 7, 2), (5, 7, 2), (6, 7, 2), (7, 7, 2), (7, 7, 1), (7, 8, 1), (8, 8, 1), (8, 9, 1), (8, 9, 0), (9, 9, 0), (10, 9, 0), (10, 8, 0), (10, 7, 0), (10, 6, 0), (11, 6, 0), (12, 6, 0), (12, 7, 0), (12, 8, 0), (13, 8, 0), (14, 8, 0), (15, 8, 0)]
    ####


if __name__ == "__main__":
    runMain()
    #runTest()