__author__ = 'Rick'

import data
import grid_copy as grid
import pathgenerator
import Visualization
import random
import time

random.seed("piemeltje")

chips = data.chips
netlist = data.netlist

final_paths = []

routes_unsorted = []  # List with start and end points of lines

for path in netlist:  # Making routes_unsorted
    chip_start = path[0]
    chip_end = path[1]
    routes_unsorted.append((chips[chip_start], chips[chip_end]))


def forceDraw(path):
    final_paths.append(pathgenerator.generateAllShortest(path[0], path[1])[0])


def calculateMinPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1])


if __name__ == "__main__":
    routes = sorted(routes_unsorted, key=calculateMinPathLength)  # Sort routes_unsorted by minimum length
    bool_grid = grid.createGrid()
    print bool_grid[0][0][0]
    for index, route in enumerate(routes):
        if index == 100:
            break
        if pathgenerator.shouldCalculateAllPaths(route[0], route[1]):
            paths = pathgenerator.generateAllShortest(route[0], route[1])
        else:
            paths = []
        for path in paths:
            random_number = random.choice(range(len(paths)))
            path = paths[random_number]
            print path
            if grid.isOccupied(path):
                print "Occupied"
                # The path is occupied
                continue  # Try next path
            # The path is free
            print "Not Occupied"
            grid.setOccupation(path, index)
            print grid.grid[15][7][3]
            final_paths.append(path)
            break  # Go to next route

    #forceDraw()

    print final_paths
    Visualization.runVisualization(final_paths)
