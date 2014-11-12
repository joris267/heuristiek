__author__ = 'Rick'

import data
import grid_copy as grid
import pathgenerator
import Visualization
import random

print "Imported"


#random.seed("poep in je mond")

chips = data.chips
netlist = data.netlist

routes_unsorted = []  # List with start and end points of lines
final_paths = []

index_path_dict = {}

for path in netlist:  # Making routes_unsorted
    chip_start = path[0]
    chip_end = path[1]
    routes_unsorted.append((chips[chip_start], chips[chip_end]))


def forceDraw(path, generate=True):
    if not generate:
        final_paths.append(path)
    else:
        final_paths.append(pathgenerator.generateAllShortest(path[0], path[1])[0])


def calculateMinPathLength(points):
    """
    Calculates the minimum path length of the route 'points'
    points = list containing one start and end point
    """
    return abs(points[0][0] - points[1][0]) + abs(points[0][1] - points[1][1])


if __name__ == "__main__":
    routes = sorted(routes_unsorted, key=calculateMinPathLength)  # Sort routes_unsorted by minimum length

    for index, route in enumerate(routes):
        if index == 7:
            break
        if pathgenerator.shouldCalculateAllPaths(route[0], route[1]):
            paths = pathgenerator.generateAllShortest(route[0], route[1])
        else:
            paths = []
        for path_number, path in enumerate(paths):
            random_number = random.choice(range(len(paths)))
            path = paths[path_number]

            if grid.isOccupied(path):
                print index, "Occupied"
                # The path is occupied

                continue  # Try next path

            # The path is free
            print index, "Not Occupied"
            grid.setOccupation(path, index)
            index_path_dict[index] = path_number, path
            #print grid.grid[15][7][3]
            final_paths.append(path)
            break  # Go to next route
    forceDraw([(2, 11, 3), (3, 11, 3), (4, 11, 3), (4, 11, 2), (5, 11, 2), (6, 11, 2), (6, 11, 3), (7, 11, 3), (8, 11, 3)], False)
    print index_path_dict
    #print final_paths
    Visualization.runVisualization(final_paths)
