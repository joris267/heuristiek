__author__ = 'Marcella Wijngaarden'

from heapq import*
import data
import grid
import Visualization
netlist = data.netlist
grid = grid.createGrid()
chips = data.chips
X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE

def getDistance(point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1]) + abs(point1[2] - point2[2])

def getCost(node, begin, end):
    g = getDistance(begin, node)
    h = getDistance(node, end)
    return g + h

def inGrid(point):
    return (0 <= point[0] < X_SIZE) and (0 <= point[1] < Y_SIZE ) and (0 <= point[2] < Z_SIZE)

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

    new_start = (x_start, y_start, z_start)
    new_end = (x_end, y_end, z_end)
    return new_start, new_end

def backTracePaths(closed_list, start, end):
    path = [end]
    astar_points = closed_list
    # print "astar_points = ", astar_points
    print start, end
    while start not in path or end not in path:
        # print "start itereation "
        # print "closed list ", closed_list
        point = path[-1]
        for check_point in astar_points:
            # parent = check_point[4]
            # next_point = check_point[3]
            # print "check_point = ", check_point
            # print "check_point[3] = ", check_point[3]
            # print "point  = ", point
            # print "distance = ", getDistance(point, check_point[3])
            if getDistance(point, check_point[3]) == 1:
                # print point, check_point[4]
                # print "here", check_point[3]
                path.append(check_point[3])
                break
    print "path is : ", path
    return path

def Astar(start, end):
    start_queue = [0, 0, 0, start, start]
    queue = [start_queue]                 # [f, g, h, (x, y, z), (parentx,y,z)]
    # heappush(queue, (3, 5))
    closed_list = []
    # print "start queue = ", queue

    while len(queue) != 0:
        heapify(queue)
        current_point = heappop(queue)

        neighbours = findNeighbours(current_point[3])

        successors = []
        for point in neighbours:

            g = current_point[1] + getCost(point, start, end)
            h = getDistance(end, point)
            f = g + h
            successors.append([f, g, h, point, current_point[4]])
            if point == end:
                print "end reached : ", point
                closed_list.append(current_point)
                closed_list.append([f, g, h, point, current_point[4]])
                paths = backTracePaths(closed_list, start, end)
                return paths, closed_list

        for successor in successors:
            for node in queue:
                if node[3] == successor[3] and successor[1] < node[1]:
                    queue.remove(node)
                    break

        for successor in successors:
            for node in closed_list:
                if len(closed_list) != 0:
                    if node[3] == successor[3] and successor[1] < node[1]:
                        closed_list.remove(node)
                        break

        for successor in successors:
            heappush(queue, successor)

        heappush(closed_list, current_point)
        # print queue, end

if __name__ == "__main__":
    netlist = data.sortDistance(netlist)
    # netlist = [netlist[i] for i in range(40, 50)]
    netlist = [netlist[40]]
    paths = []
    for net in netlist:
        start_end = calculateEndStart(chips[net[0]], chips[net[1]])
        path = Astar(start_end[0], start_end[1])
        paths.append(path[0])
    print path

    Visualization.runVisualization(paths, 0)