# Chips & Circuits case - The Chipmunks: Joris Schefold, Rick Hutten, Marcella Wijngaarden

import data as data
import pygame
import sys
import grid
from pygame.locals import *
print 'imported'

listpoints = [(1, 1, 3), (6, 1, 3), (10, 1, 3), (15, 1, 3)]  # For testing
listpoints1 = [(1, 1, 3), (1, 8, 3)]

netlist = data.netlist
chips = data.chips

shortest_paths = []

layer = 3  # For testing

X_SIZE = data.X_SIZE
Y_SIZE = data.Y_SIZE
Z_SIZE = data.Z_SIZE

SCALE = 30
GRID_WIDTH = X_SIZE*SCALE
GRID_HEIGHT = Y_SIZE*SCALE
PADDING = 30

WINDOW_WIDTH = GRID_WIDTH+300
WINDOW_HEIGHT = GRID_HEIGHT+2*PADDING
CELLSIZE = SCALE
CHIPSIZE = CELLSIZE/2

DARKGRAY = (40,40,40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Button:
    def __init__(self, text):
        self.text = text
        self.is_hover = False
        self.default_color = (100,100,100)
        self.hover_color = (255,255,255)
        self.font_color = (0,0,0)
        self.obj = None
      
    def label(self):
        """button label font"""
        font = pygame.font.Font(None, 20)
        return font.render(self.text, 1, self.font_color)
      
    def color(self):
        """change color when hovering"""
        if self.is_hover:
            return self.hover_color
        else:
            return self.default_color

    # noinspection PyUnreachableCode
    def draw(self, screen, mouse, rectcoord, labelcoord):
        """create rect obj, draw, and change color based on input"""
        self.obj  = pygame.draw.rect(screen, self.color(), rectcoord)
        screen.blit(self.label(), labelcoord)
      
        #change color if mouse over button
        self.check_hover(mouse)
      
    def check_hover(self, mouse):
        """adjust is_hover value based on mouse over button - to change hover color"""
        if self.obj.collidepoint(mouse):
            self.is_hover = True
        else:
            self.is_hover = False


def changeLayerText(layertext):
    font = pygame.font.Font(None, 42)
    text = font.render(layertext, 1, (100, 100, 0))
    DISPLAYSURF.blit(text, (GRID_WIDTH+PADDING+((WINDOW_WIDTH-GRID_WIDTH)/3.4),100))


def clearWindow():
    DISPLAYSURF.fill((0, 0, 0))
#    DISPLAYSURF.set_alpha(255)
##    rect1 = Rect(WINDOW_WIDTH,WINDOW_HEIGHT,WINDOW_WIDTH-100,WINDOW_HEIGHT-100)
##    DISPLAYSURF.blit(rect1)


def drawGrid(layer):
    """ Draws the grid for a given layer """
    for x in range(PADDING, GRID_WIDTH+CELLSIZE+PADDING, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, PADDING), (x, GRID_HEIGHT+PADDING))
    for y in range(PADDING, GRID_HEIGHT+CELLSIZE+PADDING, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (PADDING, y), (GRID_WIDTH+PADDING, y))
    if layer == 3:
        for i in range(len(chips)):
            x = (chips[i][0]*CELLSIZE)-(CHIPSIZE/2)+PADDING
            y = (chips[i][1]*CELLSIZE)-(CHIPSIZE/2)+PADDING
            pygame.draw.rect(DISPLAYSURF, RED, (x,y,CHIPSIZE,CHIPSIZE), 0)


def drawLine(pathpoints, layer):
    """ If the shortest path between two points is found, the list of connecting points
    is given to this function and these are converted to pixels and then the connecting
    line is drawn """
    path = []
    for i in range(len(pathpoints)):
        path_x = pathpoints[i][0]*CELLSIZE+PADDING
        path_y = pathpoints[i][1]*CELLSIZE+PADDING
        if pathpoints[i][2] == layer:
            path.append((path_x, path_y))
    if len(path) == 1:
        pygame.draw.circle(DISPLAYSURF, GREEN, path[0], 3, 0)
    if len(path) > 1:          
        pygame.draw.lines(DISPLAYSURF, GREEN, False, path, 2)


def drawPaths(paths, layer):
    for path in paths:
        drawLine(path, layer)
      
if __name__ == '__main__':

    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Chips & Circuits Visualization - Team Chipmunks')
    prev_btn = Button('<- Previous' )
    next_btn = Button('Next ->')
    
    for i in range(len(netlist)):
        start = chips[netlist[i][0]]
        end = chips[netlist[i][1]]
        shortest_paths.append(grid.findShortestPath(start, end))
        print start, end
    
    drawPaths(shortest_paths, layer)
        
    while True:  # main grid loop
        drawGrid(layer)
        changeLayerText("Layer #" + str(layer))
         
        mouse = pygame.mouse.get_pos()

        prev_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 2*PADDING, GRID_HEIGHT-3*PADDING, 100, 20),
                      (GRID_WIDTH + 2*PADDING+3, GRID_HEIGHT-3*PADDING+3))
        next_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 3*PADDING+100, GRID_HEIGHT-3*PADDING, 100, 20),
                      (GRID_WIDTH + 3*PADDING+103, GRID_HEIGHT-3*PADDING+3))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                 pygame.quit()
                 sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if prev_btn.obj.collidepoint(mouse) and layer > 0:
                    layer -= 1
                    changeLayerText("Layer #" + str(layer))
                    clearWindow()
                    drawPaths(shortest_paths, layer)
                    pygame.display.update()
                elif next_btn.obj.collidepoint(mouse) and layer < 7:
                    layer +=1
                    changeLayerText("Layer #" + str(layer))
                    clearWindow()
                    drawPaths(shortest_paths, layer)
                    pygame.display.update()
