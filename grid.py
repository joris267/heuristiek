import numpy as np
import time
from Visualization_test_joris import *
import pygame
import sys
from pygame.locals import *

def create_grid():
    """
    creates an grid filled with True except on the points in netlist
    will asume chips are on layer 3 unless other int is given
    imports netlist, X_SIZE, Y_SIZE and Z_SIZE from visualization
    """
    
    grid = np.ones(shape = (X_SIZE,Y_SIZE,Z_SIZE), dtype = bool)
    for chip in chip_list:
        grid[chip[0]][chip[1]][0] = False
    return grid

grid = create_grid()

#test test
