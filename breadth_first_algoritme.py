__author__ = 'Marcella Wijngaarden'
import data
import grid
import tempo
import Visualization
import time
import random
import numpy
import copy

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE
chips = data.chips
netlist = data.sortDistance(data.netlist)
path_grid = grid.createPathGrid()
grid = grid.createGrid()
relay_list = [0 for i in netlist]

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

def inGrid(point):
    return (0 <= point[0] < X_SIZE) and (0 <= point[1] < Y_SIZE) and (0 <= point[2] < Z_SIZE)

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
        original_value_start, original_value_end = tempo.isFree(start), tempo.isFree(end)
        x_start, x_end, y_start, y_end, z_start, z_end = tempo.calculateEndStart(start, end)

        start = (x_start, y_start, z_start)
        end = (x_end, y_end, z_end)
        print "Finding a path between: ", start, end

        tempo.setPathOccupation(start, -2)
        tempo.setPathOccupation(end, -2)

        path = []
        # path, grid = tempo.findPath(start, end, grid)
        if len(path) == 0:
            temp_dict[path_number] = (start, end)
        else:
            for point in path:
                tempo.setPathOccupation(point, path_number)
                tempo.setOccupation(point)
            paths_dict[path_number] = path
            paths.append(path)
        print path_number
        path_number += 1
        tempo.setPathOccupation(start, -2)
        tempo.setPathOccupation(end, -2)

    for chip in chips:
        tempo.setPathOccupation(chip, -2)

    if len(temp_dict) > 0:
        print "Trying A* method.."
        # print tempo.getPathOccupation((13, 7, 0)), 1
        for item in temp_dict:
            start, end = temp_dict[item][0], temp_dict[item][1]

            for chip in chips:
                if tempo.getPathOccupation(chip) != -2:
                    print chip, tempo.getPathOccupation(chip)
                    assert False

            # print tempo.getPathOccupation((13, 7, 0)), 0

            new_path, stuck_paths = tempo.AStartAlgoritm(start, end)[0], \
                tempo.AStartAlgoritm(start, end)[1]

            for point in new_path:
                tempo.setPathOccupation(point, item)
                tempo.setOccupation(point, False)

            # print tempo.getPathOccupation((13, 7, 0)), 3
            paths_dict[item] = new_path
            paths.append(new_path)
            tempo.setPathOccupation(start, -2)
            tempo.setPathOccupation(end, -2)

            intersection_paths.append(item)
            for stuck in stuck_paths:
                intersection_paths.append(stuck)
            # print tempo.getPathOccupation((13, 7, 0)), 2
    print 'intersection paths : ', len(intersection_paths), intersection_paths
    print 'nr of paths drawn :', len(paths_dict)
    return intersection_paths, paths_dict

def isBetterPath(new_intersections, old_path_length, new_path_length, total_paths, iterations):
    """
    Checks if a path should be constructed based on simulated annealing techniques.
    Returns True if the path should be constructed, otherwise returns False
    """
    if len(new_intersections) == 0:
        return True

    cross_value = (len(new_intersections))
    if old_path_length == 0:
        delta = 0
    else:
        delta = old_path_length - new_path_length

    # if delta > 0:
    #     percentage = (delta/100.) * (3/(2.*new_intersections))
    # if delta < 0:
    #     percentage = (1-delta/100.) * (3/(2.*new_intersections))
    # if delta == 0 or delta == 1:
    #     delta = 1
    # percentage = float(numpy.exp(cross_value/(1 - (1 / (delta*3)))))
    #percentage = float(numpy.exp((cross_value/float(new_path_length))/float(delta)))
    # percentage = numpy.exp(float(delta)/float(cross_value))

    weight = total_paths/float(len(netlist))
    # percentage = float(numpy.abs(float(numpy.cos(delta/ (float(cross_value)*weight))))) (-0.0013*iterations
    # percentage = float(numpy.abs(float(numpy.cos(delta/ (float(cross_value)*weight))))) (-0.0013*iterations
    percentage = float(numpy.exp((0.2 * delta)))/float((cross_value**0.8))
    chance = float(random.randrange(0, 100)/100.)

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
    for cross_path in intersecting_paths:
        for point in paths_dict_new[cross_path]:
            tempo.setOccupation(point)
            tempo.setPathOccupation(point, -1)
        paths_dict_new[cross_path] = []

    while len(intersecting_paths) != 0:
        counter += 1
        #index = random.randrange(1, len(intersecting_paths))
        current_path_number = random.sample(intersecting_paths, 1)[0]
        #print current_path_number
        net = netlist[current_path_number-1]

        current_path = paths_dict_new[current_path_number]
        current_path_length = len(current_path)

        print 'current path number ', current_path_number

        x_start, x_end, y_start, y_end, z_start, z_end = tempo.calculateEndStart(chips[net[0]], chips[net[1]])
        start = (x_start, y_start, z_start)
        end = (x_end, y_end, z_end)

        for point in current_path:
            tempo.setPathOccupation(point, -1)
            tempo.setOccupation(point, True)

        new_path, new_intersections_set = tempo.AStartAlgoritm(start, end)[0], tempo.AStartAlgoritm(start, end)[1]
        #print new_path

        new_intersections = []
        if len(new_intersections_set) != 0:
            for item in new_intersections_set:
                new_intersections.append(item)

        tempo.setPathOccupation(start, -2)
        tempo.setPathOccupation(end, -2)

        print 'Iteration : ', counter
        if isBetterPath(new_intersections, current_path_length, len(new_path), len(paths_dict_new), counter):
            path_counter += 1
            intersecting_paths.remove(current_path_number)
            paths_dict_new[current_path_number] = new_path
            # print 'relay path ', current_path_number

            for item in new_intersections_set:
                if item not in intersecting_paths:
                    if len(paths_dict_new[item]) != 0:
                        for point in paths_dict_new[item][1:-1]:  # all points except the endpoints are free again
                            tempo.setOccupation(point, True)
                            tempo.setPathOccupation(point, -1)
                    paths_dict_new[item] = []
                    intersecting_paths.add(item)

            for point in new_path:
                tempo.setOccupation(point)
                tempo.setPathOccupation(point, current_path_number)

            tempo.setPathOccupation(start, -2)
            tempo.setPathOccupation(end, -2)

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
                print step
                # print 'Move on because ', len(intersecting_paths), 'intersections is more than ', \
                #     len(best_situation_intersections)
                if step == 20:
                    step = 0
                    paths_dict_new = best_situation.copy()
                    intersecting_paths = best_situation_intersections.copy()
                    print 'Return to last best situation : ', len(best_situation)-len(best_situation_intersections)

            print "new_intersections ", len(new_intersections), "number of paths ", len(paths_dict_new), len(intersecting_paths), len(paths_dict_new) - len(intersecting_paths) #, new_intersections
            if len(paths_dict_new) == 50 and len(intersecting_paths) == 0:
                print paths_dict_new
                return paths_dict_new
        else:
            for point in current_path:
                tempo.setPathOccupation(point, current_path_number)
                tempo.setOccupation(point, False)

        if len(intersecting_paths) == 0:
            return paths_dict_new

        if counter == max_iteration:
            return paths_dict_new

def getTotalLength(paths):
    total = 0
    for path in paths:
        total += len(path)

    return total

if __name__ == "__main__":
    start_time = time.time()
    comp = layIntersectingPaths()
    intersecting_paths, paths_dict = comp[0], comp[1]
    paths = simulatedAnnealing(intersecting_paths, paths_dict, max_iteration=1800)
    end_time = time.time()

    # total_length = getTotalLength(paths)
    print paths
    print "Computing time = ", end_time - start_time, " seconds or ", (end_time - start_time)/60, "minutes"
    # print "Total path length : ", total_length

    layer = 0
    Visualization.runVisualization(paths.values(), layer)




