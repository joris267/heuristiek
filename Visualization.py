#C
#joris zegt weg
import numpy as np
import pygame
import sys
from pygame.locals import *
print 'imported'

X_SIZE = 17
Y_SIZE = 12
Z_SIZE = 8

listpoints = [(1,1,3),(6,1,3),(10,1,3),(15,1,3)] #For testing
listpoints1 = [(1,1,3),(1,8,3)]

shortest_paths = []

chips = [(1,1,3),(6,1,3),(10,1,3),(15,1,3),
         (3,2,3),(12,2,3),(14,2,3),
         (12,3,3),
         (8,4,3),
         (1,5,3),(4,5,3),(11,5,3),(16,5,3),

         (13,7,3),(16,7,3),
         (2,8,3),(6,8,3),(9,8,3),(11,8,3),(15,8,3),
         (1,9,3),
         (2,10,3),(9,10,3),
         (1,11,3),(12,11,3)]

netlist = [(0,13),
(0 , 14),
(0 , 22),
(1 , 7),
(3 , 19),
(3 , 9),
(4 , 8),
(4 , 9),
(5 , 14),
(5 , 4),
(6 , 10),
(6 , 17),
(7 , 23),
(10 , 0),
(10 , 1),
(10 , 18),
(10 , 18),
(11 , 0),
(11 , 17),
(11 , 3),
(11 , 4),
(11 , 9),
(12 , 24),
(13 , 4),
(14 , 19),
(14 , 21),
(16 , 16),
(16 , 23),
(16 , 7),
(17 , 15),
(17 , 21),
(17 , 9),
(18 , 20),
(18 , 21),
(18 , 23),
(18 , 5),
(18 , 9),
(19 , 20),
(19 , 21),
(20 , 6),
(21 , 15),
(21 , 2),
(22 , 10),
(22 , 11),
(22 , 18),
(22 , 4),
(23 , 4),
(23 , 5),
(24 , 15),
(24 , 16)]

layer = 3  # For testing

SCALE = 30
GRID_WIDTH = X_SIZE*SCALE
GRID_HEIGHT = Y_SIZE*SCALE
PADDING = 30

WINDOW_WIDTH = GRID_WIDTH+300
WINDOW_HEIGHT = GRID_HEIGHT+2*PADDING
CELLSIZE = SCALE
CHIPSIZE = CELLSIZE/2

DARKGRAY  = (40,40,40)
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
      '''button label font'''
      font = pygame.font.Font(None, 20)
      return font.render(self.text, 1, self.font_color)
      
   def color(self):
      '''change color when hovering'''
      if self.is_hover:
         return self.hover_color
      else:
         return self.default_color
         
   def draw(self, screen, mouse, rectcoord, labelcoord):
      '''create rect obj, draw, and change color based on input'''
      self.obj  = pygame.draw.rect(screen, self.color(), rectcoord)
      screen.blit(self.label(), labelcoord)
      
      #change color if mouse over button
      self.check_hover(mouse)
      
   def check_hover(self, mouse):
      '''adjust is_hover value based on mouse over button - to change hover color'''
      if self.obj.collidepoint(mouse):
         self.is_hover = True 
      else:
         self.is_hover = False

def changeLayerText(layertext):
    font = pygame.font.Font(None, 42)
    text = font.render(layertext, 1, (100, 100, 0))
    DISPLAYSURF.blit(text,(GRID_WIDTH+PADDING+((WINDOW_WIDTH-GRID_WIDTH)/3.4),100))

def clearWindow():
    DISPLAYSURF.fill((0,0,0))
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


def drawLine(pathpoints,layer):
    """ If the shortest path between two points is found, the list of connecting points
    is given to this function and these are converted to pixels and then the connecting
    line is drawn """
    path = []
    for i in range(len(pathpoints)):
        pathx =  pathpoints[i][0]*CELLSIZE+PADDING
        pathy =  pathpoints[i][1]*CELLSIZE+PADDING
        if pathpoints[i][2] == layer:
            path.append((pathx,pathy))
    if len(path) == 1:
        pygame.draw.circle(DISPLAYSURF, GREEN, path[0], 3, 0)
    if len(path) > 1:          
        pygame.draw.lines(DISPLAYSURF, GREEN, False, path, 2)

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

def draw_paths(paths, layer):
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
        shortest_paths.append(findShortestPath(start,end))
        print start,end
    
    draw_paths(shortest_paths,layer)
        
    while True: # main grid loop
        drawGrid(layer)
        changeLayerText("Layer #" + str(layer))
         
        mouse = pygame.mouse.get_pos()

        prev_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH+ 2*PADDING,GRID_HEIGHT-3*PADDING,100,20), (GRID_WIDTH+ 2*PADDING+3,GRID_HEIGHT-3*PADDING+3))  
        next_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH+ 3*PADDING+100,GRID_HEIGHT-3*PADDING,100,20), (GRID_WIDTH+ 3*PADDING+103,GRID_HEIGHT-3*PADDING+3))  
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
                    draw_paths(shortest_paths,layer)
                    pygame.display.update()
                elif next_btn.obj.collidepoint(mouse) and layer < 7:
                    layer +=1
                    changeLayerText("Layer #" + str(layer))
                    clearWindow()
                    draw_paths(shortest_paths,layer)
                    pygame.display.update()
