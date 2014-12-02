import time
import data
import grid_copy as grid
from heapq import *
import Visualization

chips = data.chips
netlist = data.netlist
data_grid = grid.grid


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
            if grid.inGrid(neighbour):
                neighbours.append(neighbour)
    return neighbours

def minPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1]) + abs(points[0][2] - points[1][2])


def aStar(point1, point2, line_val):
    queue = []  # (f, g, h, point, path_to_point), point = (x, y, z)
    g = 0
    h = minPathLength((point1, point2))
    f = g + h
    heappush(queue, (f, g, h, point1, [point1]))

    while queue != []:
        q = heappop(queue)

        for no, successor in enumerate(findNeighbours(q[3])):
            if successor == point2:
                print "Pad gevonden!"
                print q[4] + [successor]
                return q[4] + [successor]
            g = q[1] + 1
            h = minPathLength((successor, point2))
            f = g + h
            if grid.isOccupied(successor):
                continue

            item = (f, g, h, successor, q[4] + [successor])
            heappush(queue, item)

        grid.setPointOccupation(q[3], line_val)
    print "Path not found"
    return []


if __name__ == "__main__":
    start = time.clock()
    path = aStar((1, 1, 0), (15, 8, 0), 1)
    path2 = aStar((6, 1, 0), (9, 10, 0), 2)
    print time.clock() - start

    Visualization.run3DVisualisation([path, path2], 3)