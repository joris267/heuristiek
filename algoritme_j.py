import numpy as np
import random
import data_test


class PathLengthError(Exception):
    def __init__(self):
        pass

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
        print "point ", point, "lies outside of grid"
        return False
    return value

def setOccupation(point, occupation = False):
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
    setOccupation(end, True)
    setOccupation(start, True)
    occupied_points = len(findOccupiedPoints())

    path_points = [start]
    setOccupation(start)
    path_found = False
    current_point = start

    while not path_found:
        # print "path: ", path_points

        if len(path_points) > 50:
            print "path to long"
            for point in path_points:
                setOccupation(point, True)
            raise PathLengthError()

        # randomizes the order in which a path wil be sought in the x, y and z direction
        dimensions = 2
        if current_point[2] != end[2]:
            dimensions += 1
        dimensions = range(dimensions)
        random.shuffle(dimensions)

        # to check if there is any way in which the path can move the current point is safed and compared at the end
        # of the searth for the path in all directions
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
        assert occupied_points + len(path_points) == len(findOccupiedPoints())
        if last_point == current_point:
            free_neighbours = freeNeighbour(current_point)
            if len(free_neighbours) == 0:
                print "stuck"
                return path_points, grid

            current_point = random.choice(free_neighbours)
            path_points.append(current_point)
            setOccupation(current_point)

        assert occupied_points + len(path_points)  == len(findOccupiedPoints())

        if current_point == end:
            print "found: ", path_points, "occupied" ,findOccupiedPoints()
            return path_points, grid


if __name__ == "__main__":
    grid = createGrid()
