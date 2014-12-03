# Chips & Circuits case - The Chipmunks: Joris Schefold, Rick Hutten, Marcella Wijngaarden
import data as data
import pygame
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

netlist = data.netlist  # The paths that need to be drawn
chips = data.chips    # The chips on the grid

layer = 0  # The layer that is drawn first

X_SIZE = data.X_SIZE-1  #
Y_SIZE = data.Y_SIZE-1  # Dimensions of the grid
Z_SIZE = data.Z_SIZE  #

SCALE = 30
GRID_WIDTH = X_SIZE * SCALE
GRID_HEIGHT = Y_SIZE * SCALE
LINE_WIDTH = 4  # Preferably an even number
PADDING = 30

WINDOW_WIDTH = GRID_WIDTH + 300
WINDOW_HEIGHT = GRID_HEIGHT + (2 * PADDING)
CELLSIZE = SCALE
CHIPSIZE = CELLSIZE / 2

BLUE = (0, 0, 255)            # Down color
RED = (255, 0, 0)             # Up color
LIGHT_GRAY = (125, 125, 125)  # Chip-color
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
    if layer_number == 0:
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
                for point in path:  # Purely for aesthetic reasons, the edges of the lines are now rounded
                    pygame.draw.circle(DISPLAYSURF, line_color, (point[0]+1, point[1]+1), LINE_WIDTH/2, 0)
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
            for point in path:  # Purely for aesthetic reasons, the edges of the lines are now rounded
                pygame.draw.circle(DISPLAYSURF, line_color, (point[0]+1, point[1]+1), LINE_WIDTH/2, 0)


def drawPaths(paths, layer_number):
    for index, path in enumerate(paths):
        drawLine(path, layer_number, index)


def runVisualization(paths, active_layer = 0):
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


def run3DVisualisation(paths, file_name="untitled"):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for chip in data.chips:
        chip_x = chip[0]
        chip_y = chip[1]
        ax.scatter(chip_x, chip_y, s=30, c='r')

    for path in paths:
        x = []
        y = []
        z = []
        for point in path:
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])
        ax.plot(x, y, z, markersize=20)

    ax.set_xlim(0, X_SIZE)
    ax.set_xticks(range(X_SIZE + 1))
    ax.set_xticklabels(range(X_SIZE + 1), alpha=0.0)
    ax.set_ylim(0, Y_SIZE)
    ax.set_yticks(range(Y_SIZE + 1))
    ax.set_yticklabels(range(X_SIZE + 1), alpha=0.0)
    ax.set_zlim(0, Z_SIZE - 1)
    ax.set_frame_on(False)
    ax.set_zlabel("Layer")
    plt.show()
    #plt.savefig(str(file_name) + ".png", format="png")
    plt.close()