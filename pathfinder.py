import pygame
from queue import PriorityQueue

GRID_WIDTH = 700
PANEL_WIDTH = 100
WIN = pygame.display.set_mode((GRID_WIDTH + PANEL_WIDTH, GRID_WIDTH + PANEL_WIDTH))

# putting controls in the caption
pygame.display.set_caption("Left click: place nodes | right click: remove nodes | space: start pathfinder | c: reset grid")

CLOSED_COLOR = (239, 143, 117) # closed
OPEN_COLOR = (17, 46, 61) # open
EMPTY_COLOR = (247, 236, 189) # empty
WALL_COLOR = (175, 192, 159) # wall
WALL2_COLOR = (165, 184, 147)
PATH_COLOR = (192, 68, 68) # path
START_COLOR = (192, 68, 68) # start
GRID_COLOR = (247, 236, 189) # lines
END_COLOR = (192, 68, 68) # end

class Node:
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = EMPTY_COLOR
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == CLOSED_COLOR

    def is_open(self):
        return self.color == OPEN_COLOR

    def is_wall(self):
        return self.color == WALL_COLOR

    def is_start(self):
        return self.color == START_COLOR

    def is_end(self):
        return self.color == END_COLOR

    def reset(self):
        self.color = EMPTY_COLOR

    def make_closed(self):
        self.color = CLOSED_COLOR

    def make_open(self):
        self.color = OPEN_COLOR

    def make_wall(self):
        self.color = WALL_COLOR

    def make_start(self):
        self.color = START_COLOR

    def make_end(self):
        self.color = END_COLOR

    def make_path(self):
        self.color = PATH_COLOR

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        # Initialize list of neighbors to this node
        self.neighbors = []

        # check neighbor below
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall(): 
            self.neighbors.append(grid[self.row + 1][self.col])

        # check neighbor above
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall(): 
            self.neighbors.append(grid[self.row - 1][self.col])

        # check neighbor to left
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall(): 
            self.neighbors.append(grid[self.row][self.col + 1])

        # check neighbor to right
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall(): 
            self.neighbors.append(grid[self.row][self.col - 1])

def h(p1, p2):
    # Manhatten distance
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    # current begins as the end node and traverses the dictionary backwards making a path
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_position(), end.get_position())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

        # The end was found so we can reconstruct the path
		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

        # check the potential g scores for each neighbor to the current node
		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_position(), end.get_position())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    # space between lines
    gap = width // rows 

    for i in range(rows):

        # draw Horizontal lines
        pygame.draw.line(win, GRID_COLOR, (0, i*gap), (width, i * gap))

        # draw Vertical lines
        pygame.draw.line(win, GRID_COLOR, (i * gap, 0), (i * gap, width))
        
def draw(win, grid, rows, width):

    # draw background
    win.fill(EMPTY_COLOR)
    win_size = GRID_WIDTH + PANEL_WIDTH
    pygame.draw.rect(win, WALL_COLOR, (GRID_WIDTH, 0, win_size, GRID_WIDTH))
    pygame.draw.rect(win, WALL_COLOR, (0, GRID_WIDTH, win_size, win_size))
    pygame.draw.line(win, WALL2_COLOR, (GRID_WIDTH, GRID_WIDTH), (win_size, win_size), width=15)

    # draw the nodes
    for row in grid:
        for node in row:
            node.draw(win)

    # draw the grid lines
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_position(position, rows, width):
    gap = width // rows
    y, x = position

    row = y // gap
    col = x // gap

    if row >= rows or col >= rows:
        return -1, -1

    return row, col

def main(win, width):
    ROWS = 70
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:

        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # left click to add node
            if pygame.mouse.get_pressed()[0]:

                # determine the node at position of click
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                if row == -1:
                    continue
                node = grid[row][col]

                # start node not set
                if not start and node != end:
                    start = node
                    start.make_start()
                    continue

                # end node not set
                if not end and node != start:
                    end = node
                    end.make_end()
                    continue

                elif node != start and node != end:
                    node.make_wall()

            # right click to remove node
            elif pygame.mouse.get_pressed()[2]:

                # determine the node at position of click
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            # space bar to start path finding
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # reset visualization
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, GRID_WIDTH)