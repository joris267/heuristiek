import numpy as np
import data as data
from pygame.locals import *

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE

chips = data.chips

def create_grid():
    """
    creates an grid filled with True except on the points in netlist
    will asume chips are on layer 3 unless other int is given
    imports netlist, X_SIZE, Y_SIZE and Z_SIZE from visualization
    """
    
    grid = np.ones(shape = (X_SIZE,Y_SIZE,Z_SIZE), dtype = bool)
    for chip in chips:
        grid[chip[0]][chip[1]][0] = False
    return grid

def findShortestPath(start,end):
    """ Algorithm that finds shortest intersecting path between 2 points
     Returns a list of points that make up the shortest path in one layer"""

    x_start = min([start[0], end[0]])
    if x_start == start[0]:
       x_end = end[0]
       y_start = start[1]
       y_end = end[1]
    else:
       x_end = start[0]
       y_start = end[1]
       y_end = start[1]

    path_points = []

    for i in range(x_end - x_start + 1):
        path_points.append((x_start + i, y_start, start[2]))

    if y_end != y_start:
        direction = (y_end-y_start)/abs(y_end-y_start) #-1 or 1
        for j in range(0,y_end - y_start + direction, direction):
            path_points.append((x_end, y_start + j, end[2]))
    return path_points
