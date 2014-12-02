import time
import data
import grid_copy as grid
from heapq import *
import Visualization

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
    visited_points = []
    heappush(queue, (f, g, h, point1, [point1]))

    while queue != []:
        q = heappop(queue)

        for no, successor in enumerate(findNeighbours(q[3])):
            if successor in visited_points:
                continue
            visited_points.append(successor)
            if successor == point2:
                return q[4] + [successor]
            g = q[1] + 1
            h = minPathLength((successor, point2))
            f = g + h
            if grid.isOccupied(successor):
                continue

            item = (f, g, h, successor, q[4] + [successor])
            heappush(queue, item)

        #rid.setPointOccupation(q[3], line_val)
    print "Path not found"
    return []


def main():
    netlist_sorted = sorted(nets_unsorted, key=minPathLength)  # Sort nets_unsorted by minimum length

    for index, net in enumerate(netlist_sorted):
        print index

        path = aStar(net[0], net[1], index)
        grid.setOccupation(path, index)
        if path != []:
            final_paths[index] = path

    return final_paths.values()

if __name__ == "__main__":
    start = time.clock()
    paths = main()
    print "Calculated in:", time.clock() - start

    Visualization.run3DVisualisation(paths)