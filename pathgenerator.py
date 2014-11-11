__author__ = 'Rick'

import copy
import math
import time


def shouldCalculateAllPaths(point1, point2):
    if calculateNumberOfPaths(point1, point2) < 500:
        return True
    return False


def calculateNumberOfPaths(point1, point2):
    """
    !!! This function ignores the z-component of both points !!!
    Estimates the number of available shortest paths between point1 and point2
    A normal computer would calculate about 5000 to 8000 paths per second (my crappy machine anyway)
    """
    x = abs(point2[0] - point1[0]) + 0.0001
    y = abs(point2[1] - point1[1]) + 0.0001
    return int(round(0.19 * pow(x, pow(y, 0.47)) * pow(y, pow(x, 0.47)) + 0.264 * math.exp(pow(x*y, 0.5))))


def generateAllShortest(point1, point2):
    """
    !!! This function ignores the z-component of both points !!!
    Calculates all the shortest paths between point1 and point2
    """
    possible_paths = [[point1]]
    done = False
    while not done:
        done_paths = 0
        for path in possible_paths:
            if path[-1] == point2:
                done_paths += 1
                if done_paths == len(possible_paths):
                    done = True
                    break
                continue
            else:
                for number, next_path in enumerate(findNextPoints(path[-1], point2)):
                    if number == 0:
                        path.append(next_path)
                    if number == 1:
                        path2 = copy.deepcopy(path)
                        path2[-1] = next_path
                        possible_paths.append(path2)
    return possible_paths


def findNextPoints(point1, point2):
    """
    Returns all the points that are available for the next step (for the shortest path)
    """
    next_points = []
    if point2[0] - point1[0] > 0:
        next_points.append(_goRight(point1))
    if point2[0] - point1[0] < 0:
        next_points.append(_goLeft(point1))
    if point2[1] - point1[1] > 0:
        next_points.append(_goDown(point1))
    if point2[1] - point1[1] < 0:
        next_points.append(_goUp(point1))
    return next_points


def _goUp(point):
    """
    Returns the point above the given point
    """
    return point[0], point[1] - 1, point[2]


def _goDown(point):
    """
    Returns the point below the given point
    """
    return point[0], point[1] + 1, point[2]


def _goLeft(point):
    """
    Returns the point left of the given point
    """
    return point[0] - 1, point[1], point[2]


def _goRight(point):
    """
    Returns the point right of the given point
    """
    return point[0] + 1, point[1], point[2]


if __name__ == "__main__":

    _points = [(3, 2, 3), (8, 7, 3)]
    _point_one = _points[0]
    _point_two = _points[1]
    _delta_x = _point_two[0]
    _delta_y = _point_two[1]

    print "From", _point_one, "to " + str(_point_two) + ":"
    print "Number of paths:"
    print "Estimation:", calculateNumberOfPaths(_point_one, _point_two)
    _start = time.clock()
    _a = generateAllShortest(_point_one, _point_two)
    _total_time = time.clock() - _start
    print "Exact:", len(_a)
    print "All paths calculated in:", _total_time, "seconds."
    print "\nPath length:", len(_a[0])
    print _a[0]
