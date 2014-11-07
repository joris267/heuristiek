# Chips & Circuits case - The Chipmunks: Joris Schefold, Rick Hutten, Marcella Wijngaarden

import data as data
import pygame
import sys
import grid

print 'imported'

listpoints = [[(1, 1, 3), (1, 2, 3), (1, 3, 3), (1, 4, 3), (1, 5, 3),
               (1, 5, 4), (2, 5, 4), (3, 5, 4), (4, 5, 4),
               (4, 5, 3), (5, 5, 3), (6, 5, 3), (6, 6, 3),
               (6, 6, 2), (5, 6, 2), (4, 6, 2), (3, 6, 2), (3, 5, 2), (3, 4, 2),
               (3, 4, 3), (3, 3, 3),
               (3, 3, 4),
               (3, 3, 5), (3, 4, 5)]]

netlist = data.netlist  # The paths that need to be drawn
chips = data.chips  # The chips on the grid
layer = 3  # The layer that is drawn first
X_SIZE = data.X_SIZE  #
Y_SIZE = data.Y_SIZE  # Dimension of the grid
Z_SIZE = data.Z_SIZE  #

SCALE = 30
GRID_WIDTH = X_SIZE * SCALE
GRID_HEIGHT = Y_SIZE * SCALE
PADDING = 30

WINDOW_WIDTH = GRID_WIDTH + 300
WINDOW_HEIGHT = GRID_HEIGHT + (2 * PADDING)
CELLSIZE = SCALE
CHIPSIZE = CELLSIZE / 2

DARKGRAY = (40, 40, 40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

COLOR_DOWN = BLUE
COLOR_UP = RED
LINE_COLOR = WHITE
CHIP_COLOR = GREEN


class Button:
    def __init__(self, text):
        self.text = text
        self.is_hover = False
        self.default_color = (100, 100, 100)
        self.hover_color = (255, 255, 255)
        self.font_color = (0, 0, 0)
        self.obj = None

    def label(self):
        """
        Button label font
        """
        font = pygame.font.Font(None, 20)
        return font.render(self.text, 1, self.font_color)

    def color(self):
        """
        Change color when hovering
        """
        if self.is_hover:
            return self.hover_color
        else:
            return self.default_color

    def draw(self, screen, mouse_object, rectcoord, labelcoord):
        """
        Create rect obj, draw, and change color based on input
        """
        self.obj = pygame.draw.rect(screen, self.color(), rectcoord)
        screen.blit(self.label(), labelcoord)

        # change color if mouse over button
        self.checkHover(mouse_object)

    def checkHover(self, mouse_object):
        """
        Adjust is_hover value based on mouse over button - to change hover color
        """
        if self.obj.collidepoint(mouse_object):
            self.is_hover = True
        else:
            self.is_hover = False


def changeLayerText(layertext):
    font = pygame.font.Font(None, 42)
    text = font.render(layertext, 1, (100, 100, 0))
    DISPLAYSURF.blit(text, (GRID_WIDTH + PADDING + ((WINDOW_WIDTH - GRID_WIDTH) / 3.4), 100))


def clearWindow():
    DISPLAYSURF.fill((0, 0, 0))


# DISPLAYSURF.set_alpha(255)
# rect1 = Rect(WINDOW_WIDTH,WINDOW_HEIGHT,WINDOW_WIDTH-100,WINDOW_HEIGHT-100)
#    DISPLAYSURF.blit(rect1)


def drawGrid(layer_number):
    """
    Draws the grid for a given layer and chips
    """
    for x in range(PADDING, GRID_WIDTH + CELLSIZE + PADDING, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, PADDING), (x, GRID_HEIGHT + PADDING))
    for y in range(PADDING, GRID_HEIGHT + CELLSIZE + PADDING, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (PADDING, y), (GRID_WIDTH + PADDING, y))
    if layer_number == 3:
        for j in range(len(chips)):
            x = (chips[j][0] * CELLSIZE) - (CHIPSIZE / 2) + PADDING
            y = (chips[j][1] * CELLSIZE) - (CHIPSIZE / 2) + PADDING
            pygame.draw.rect(DISPLAYSURF, CHIP_COLOR, (x, y, CHIPSIZE, CHIPSIZE), 0)


def drawLine(pathpoints, layer_number):
    """
    If the shortest path between two points is found, the list of connecting points
    is given to this function and these are converted to pixels and then the connecting
    line is drawn
    """
    path = []
    for k in range(len(pathpoints)):
        path_x = pathpoints[k][0] * CELLSIZE + PADDING
        path_y = pathpoints[k][1] * CELLSIZE + PADDING

        if pathpoints[k][2] == layer_number:
            path.append((path_x, path_y))
        elif path:  # Else if path is not empty (path != [])
            # Draw the path
            if len(path) == 1:
                pygame.draw.circle(DISPLAYSURF, LINE_COLOR, path[0], 5, 0)
            if len(path) > 1:
                pygame.draw.lines(DISPLAYSURF, LINE_COLOR, False, path, 2)
            path = []

        try:  # See if this point went up or down
            if pathpoints[k - 1][2] < layer_number:
                pygame.draw.circle(DISPLAYSURF, COLOR_DOWN, path[-1], 5, 0)
            if pathpoints[k - 1][2] > layer_number:
                pygame.draw.circle(DISPLAYSURF, COLOR_UP, path[-1], 5, 0)
        except IndexError:
            # This is the first point
            pass
        try:  # See if the next point goes up or down
            if pathpoints[k + 1][2] < layer_number:
                pygame.draw.circle(DISPLAYSURF, COLOR_DOWN, path[-1], 5, 0)
            if pathpoints[k + 1][2] > layer_number:
                pygame.draw.circle(DISPLAYSURF, COLOR_UP, path[-1], 5, 0)
        except IndexError:
            # This is the last point
            pass

    if path:
        # Draw the last path
        if len(path) == 1:
            pygame.draw.circle(DISPLAYSURF, LINE_COLOR, path[0], 3, 0)
        if len(path) > 1:
            pygame.draw.lines(DISPLAYSURF, LINE_COLOR, False, path, 2)


def drawPaths(paths, layer_number):
    for path in paths:
        drawLine(path, layer_number)


def runVisualization(paths, active_layer = 3):
    global DISPLAYSURF, WINDOW_WIDTH, WINDOW_HEIGHT, GRID_WIDTH, PADDING, GRID_HEIGHT
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Chips & Circuits Visualization - Team Chipmunks')
    prev_btn = Button('<- Previous')
    next_btn = Button('Next ->')

    # Draw the visualisation the first time
    drawGrid(active_layer)
    changeLayerText("Layer #" + str(active_layer))
    drawPaths(paths, active_layer)

    while True:  # Main loop
        mouse = pygame.mouse.get_pos()

        prev_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 2 * PADDING, GRID_HEIGHT - 3 * PADDING, 100, 20),
                      (GRID_WIDTH + 2 * PADDING + 3, GRID_HEIGHT - 3 * PADDING + 3))
        next_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 3 * PADDING + 100, GRID_HEIGHT - 3 * PADDING, 100, 20),
                      (GRID_WIDTH + 3 * PADDING + 103, GRID_HEIGHT - 3 * PADDING + 3))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if prev_btn.obj.collidepoint(mouse) and active_layer > 0:
                    layer -= 1
                    clearWindow()
                    drawGrid(layer)
                    changeLayerText("Layer #" + str(layer))
                    drawPaths(paths, layer)
                    pygame.display.update()
                elif next_btn.obj.collidepoint(mouse) and active_layer < 7:
                    layer += 1
                    clearWindow()
                    drawGrid(layer)
                    changeLayerText("Layer #" + str(layer))
                    drawPaths(paths, layer)
                    pygame.display.update()


if __name__ == '__main__':
    shortest_paths = grid.theoreticalShortestPaths(netlist)
    print "The total wire length is %i and there are %i intersections of which there are %i on the endpoints" % (
        grid.calculateWireLenght(shortest_paths), grid.checkIntsections(shortest_paths), grid.doubleStartEndPoints(netlist))

    runVisualization(shortest_paths, layer)
