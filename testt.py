__author__ = 'Rick'

import data
import pathgenerator

chips = data.chips
netlist = data.netlist

big_number = 50  # The amount of possible paths that is considered 'big'. Change this number

no_of_paths_list = []

for connection in netlist:
    point_one = chips[connection[0]]
    point_two = chips[connection[1]]
    number = pathgenerator.calculateNumberOfPaths(point_one, point_two)
    no_of_paths_list.append(number)
    if number > big_number:
        # Print the two chips with many possible paths,
        # and the amount of possible paths
        print point_one, point_two, "Amount", number


bigger = 0
for number in no_of_paths_list:
    if number > big_number:
        bigger += 1

print "Total number of paths:", len(no_of_paths_list)
print "Number of paths smaller than " + str(big_number) + ":", len(no_of_paths_list) - bigger
print "Number of paths bigger than " + str(big_number) + ":", bigger

print range(1, 10)

###############################


# Chips & Circuits case - The Chipmunks: Joris Schefold, Rick Hutten, Marcella Wijngaarden

import data as data
import pygame

netlist = data.netlist  # The paths that need to be drawn
chips = data.chips      # The chips on the grid

layer = 3  # The layer that is drawn first

X_SIZE = data.X_SIZE  #
Y_SIZE = data.Y_SIZE  # Dimensions of the grid
Z_SIZE = data.Z_SIZE  #

SCALE = 30
GRID_WIDTH = X_SIZE * SCALE
GRID_HEIGHT = Y_SIZE * SCALE
LINE_WIDTH = 4
PADDING = 30

WINDOW_WIDTH = GRID_WIDTH + 300
WINDOW_HEIGHT = GRID_HEIGHT + (2 * PADDING)
CELLSIZE = SCALE
CHIPSIZE = CELLSIZE / 2

BLUE = (0, 0, 255)            # Down color
RED = (255, 0, 0)             # Up color
LIGHT_GRAY = (105, 105, 105)  # Chip-color
DARKGRAY = (40, 40, 40)       # Grid lines color

CHOCOLATE = (210, 105, 30)          # Brownish orange
LIGHT_STEEL_BLUE = (176, 196, 222)  # Metallic blue
PALE_VIOLET_RED = (219, 112, 147)   # Pale pink
SLATE_BLUE = (106, 90, 205)         # Purple-ish blue
CORN_FLOWER_BLUE = (100, 149, 237)  # Light blue
SALMON = (250, 128, 114)            # Pinky
KHAKI = (240, 230, 140)             # Light brown
PEACH_PUFF = (255, 218, 185)        # Light orange pinky
VIOLET = (238, 130, 238)            # Pink/violet
SADDLE_BROWN = (139, 69, 19)        # Brown
LIME_GREEN = (50, 205, 50)          # Not-so-bright green


COLOR_DOWN = BLUE
COLOR_UP = RED
CHIP_COLOR = LIGHT_GRAY

line_colors = [CHOCOLATE, LIGHT_STEEL_BLUE, PALE_VIOLET_RED, SLATE_BLUE, CORN_FLOWER_BLUE, SALMON, KHAKI, PEACH_PUFF,
               VIOLET, SADDLE_BROWN, LIME_GREEN]


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


def drawLine(pathpoints, layer_number, index):
    """
    If the shortest path between two points is found, the list of connecting points
    is given to this function and these are converted to pixels and then the connecting
    line is drawn
    """
    index %= len(line_colors)
    line_color = line_colors[index]

    path = []
    for k in range(len(pathpoints)):
        path_x = pathpoints[k][0] * CELLSIZE + PADDING
        path_y = pathpoints[k][1] * CELLSIZE + PADDING

        if pathpoints[k][2] == layer_number:
            path.append((path_x, path_y))
        elif path:  # Else if path is not empty (path != [])
            # Draw the path
            if len(path) == 1:
                pygame.draw.circle(DISPLAYSURF, line_color, path[0], 5, 0)
            if len(path) > 1:
                pygame.draw.lines(DISPLAYSURF, line_color, False, path, LINE_WIDTH)
            path = []

        try:  # See if this point went up or down
            if pathpoints[k - 1][2] < layer_number and k != 0:
                pygame.draw.circle(DISPLAYSURF, COLOR_DOWN, path[-1], 5, 0)
            if pathpoints[k - 1][2] > layer_number and k != 0:
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
            pygame.draw.circle(DISPLAYSURF, line_color, path[0], 5, 0)
        if len(path) > 1:
            pygame.draw.lines(DISPLAYSURF, line_color, False, path, LINE_WIDTH)


def drawPaths(paths, layer_number):
    for index, path in enumerate(paths):
        drawLine(path, layer_number, index)


def runVisualization(paths, active_layer=3):
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

    done = False
    while not done:  # Main loop
        mouse = pygame.mouse.get_pos()

        prev_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 2 * PADDING, GRID_HEIGHT - 3 * PADDING, 100, 20),
                      (GRID_WIDTH + 2 * PADDING + 3, GRID_HEIGHT - 3 * PADDING + 3))
        next_btn.draw(DISPLAYSURF, mouse, (GRID_WIDTH + 3 * PADDING + 100, GRID_HEIGHT - 3 * PADDING, 100, 20),
                      (GRID_WIDTH + 3 * PADDING + 103, GRID_HEIGHT - 3 * PADDING + 3))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if prev_btn.obj.collidepoint(mouse) and active_layer > 0:
                    active_layer -= 1
                    clearWindow()
                    drawGrid(active_layer)
                    changeLayerText("Layer #" + str(active_layer))
                    drawPaths(paths, active_layer)
                    pygame.display.update()
                elif next_btn.obj.collidepoint(mouse) and active_layer < 7:
                    active_layer += 1
                    clearWindow()
                    drawGrid(active_layer)
                    changeLayerText("Layer #" + str(active_layer))
                    drawPaths(paths, active_layer)
                    pygame.display.update()
    pygame.quit()

#############################

__author__ = 'Rick'

import copy
import math
import time


def shouldCalculateAllPaths(point1, point2):
    if calculateNumberOfPaths(point1, point2) < 5000:
        return True
    return False


def calculateNumberOfPaths(point1, point2):
    """
    !!! This function ignores the z-component of both points !!!
    Estimates the number of available shortest paths between point1 and point2
    A normal computer would calculate about 5000 to 8000 paths per second (my crappy machine anyway)
    """
    x = abs(point2[0] - point1[0]) + 0.0001  # '+0.0001' is necessary because 0^0 is undefined
    y = abs(point2[1] - point1[1]) + 0.0001  # and is doesn't contribute to the result
    return int(round(0.19 * pow(x, pow(y, 0.47)) * pow(y, pow(x, 0.47)) + 0.264 * math.exp(pow(x*y, 0.5))))


def pathComplexity(path):
    complexity = 0
    x_changed = False
    y_changed = False
    for index in range(1, len(path)):
        if path[index][0] == path[index - 1][0]:
            if x_changed:
                complexity += 1
            x_changed = False
            y_changed = True
        elif path[index][1] == path[index - 1][1]:
            if y_changed:
                complexity += 1
            x_changed = True
            y_changed = False
    return complexity


def generateAllShortest(point1, point2):
    """
    !!! This function ignores the z-component of both points !!!
    Calculates all the shortest paths between point1 and point2 and sorts them by omplexity
    """
    possible_paths = [[point1]]
    done = False
    while not done:
        done_paths = 0
        for path in possible_paths:
            if path[-1] == point2:
                done_paths += 1
                if done_paths == len(possible_paths):
                    done = True
                    break
                continue
            else:
                for number, next_path in enumerate(findNextPoints(path[-1], point2)):
                    if number == 0:
                        path.append(next_path)
                    if number == 1:
                        path2 = copy.deepcopy(path)
                        path2[-1] = next_path
                        possible_paths.append(path2)
    return sorted(possible_paths, key=pathComplexity)


def findNextPoints(point1, point2):
    """
    Returns all the points that are available for the next step (for the shortest path)
    """
    next_points = []
    if point2[0] - point1[0] > 0:
        next_points.append(_goRight(point1))
    if point2[0] - point1[0] < 0:
        next_points.append(_goLeft(point1))
    if point2[1] - point1[1] > 0:
        next_points.append(_goDown(point1))
    if point2[1] - point1[1] < 0:
        next_points.append(_goUp(point1))
    return next_points


def _goUp(point):
    """
    Returns the point above the given point
    """
    return point[0], point[1] - 1, point[2]


def _goDown(point):
    """
    Returns the point below the given point
    """
    return point[0], point[1] + 1, point[2]


def _goLeft(point):
    """
    Returns the point left of the given point
    """
    return point[0] - 1, point[1], point[2]


def _goRight(point):
    """
    Returns the point right of the given point
    """
    return point[0] + 1, point[1], point[2]


if __name__ == "__main__":

    _points = [(3, 2, 3), (14, 8, 3)]
    _point_one = _points[0]
    _point_two = _points[1]
    _delta_x = _point_two[0]
    _delta_y = _point_two[1]

    print "From", _point_one, "to " + str(_point_two) + ":"
    print "Number of paths:"
    print "Estimation:", calculateNumberOfPaths(_point_one, _point_two)
    _start = time.clock()
    _a = generateAllShortest(_point_one, _point_two)
    _total_time = time.clock() - _start
    print "Exact:", len(_a)
    print "All paths calculated in:", _total_time, "seconds."
    print "\nPath length:", len(_a[0]) - 1
    print _a[0]
    print "Complexity a[0]:", pathComplexity(_a[2])