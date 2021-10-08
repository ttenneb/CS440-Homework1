import heapq
from random import random

import pygame
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = [128, 128, 128]
WIDTH = 707
SIZE = 101
BLOCK_SIZE = WIDTH // SIZE
LINE_WIDTH = 2


class Tile:  # class for each tile, each tile is defined by an (x,y) coordinate as seperate x and y values
    def __init__(self, x, y):
        self.neighbors = []  # neighbors list to iterate through nerighbors
        self.x = x
        self.y = y
        self.initialize = False
        self.is_block = False
        self.color = WHITE

        self.f = 0
        self.g = 100000
        self.h = 0
        self.closed = False
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

    def __gt__(self, other):
        return self.f > other.f

    def get_color(self):  # dont really use this method
        return self.color

    def color_in(self, window):  # use this method to color in each block
        pygame.draw.rect(window, self.color, [self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])

    def get_position(self):  # returns the x and y coordinate, useful for comparing two tiles
        return self.x, self.y

    def compare_to(self, t):  # compares two tiles, useful for seeing if the tile has already been initialized
        return self.x == t.x and self.y == t.y

    def add_neighbors(self, t):  # adds neighbor for both tiles that are connected via edge
        for n in self.neighbors:  # check all neighbors in list
            if n.compare_to(t):
                return  # neighbor in list already, do nothing

        self.neighbors.append(t)  # add t to neighbors list
        t.neighbors.append(self)  # add this node to t node's neighbors list


class BinaryHeap:
    # parent is at i // 2
    # left child is at 2*i + 1
    # right child is at 2*i + 2
    def __init__(self, size):
        self.size = size
        self.index = 0
        self.heap = [None] * size

    def get_size(self):
        return self.index

    def insert(self, data):
        if self.heap[self.index] is None:
            self.heap[0] = data
        else:
            self.index = self.index + 1
            self.heap[self.index] = data
            self.bubble_up(self.index)

    def extract(self) -> Tile:
        minVal = self.heap[0]  # take min value
        temp = self.heap[self.index]  # swap last value with the first value
        self.heap[self.index] = None
        self.index = self.index - 1
        self.heap[0] = temp
        self.sift_down(0)  # perform siftdown
        return minVal

    def sift_down(self, i):
        j = i
        L = 2 * i + 1
        r = 2 * i + 2

        if L <= self.index:  # if index is left most and you say R <= index because index can be at left and this would be false
            if self.heap[L].f < self.heap[j].f:
                temp = self.heap[j].f
                self.heap[j].f = self.heap[L].f
                self.heap[L].f = temp
                self.sift_down(L)
            elif self.heap[r].f < self.heap[j].f:
                temp = self.heap[j].f
                self.heap[j].f = self.heap[r].f
                self.heap[r].f = temp
                self.sift_down(r)
            else:
                return

    def print(self):
        for element in self.heap:
            print(element)

    def bubble_up(self, i):  # i is the index of the last node inserted (size)
        j = i
        p = j // 2

        if i > 0:  # make sure node is not the root node - root node has no parents to examine
            if self.heap[j].f < self.heap[p].f:  # child is less than the parent
                temp = self.heap[p].f  # swap child with parent
                self.heap[p].f = self.heap[j].f
                self.heap[j].f = temp
                self.bubble_up(p)  # call bubble up on the p index now


class Graph:
    def __init__(self, size):
        self.rows = size
        self.columns = size
        self.vertices = []

    def add_edge(self, t1, t2):
        pass


def draw_main(window, grid):  # draws the tiles and their color
    window.fill(BLACK)
    for row in grid:
        for t in row:
            t.color_in(window)  # color in tile method
    draw_grid_lines(window)  # draws the grid lines
    pygame.display.update()  # updates pygame


def draw_grid_lines(win):  # draws the grid lines that seperate each tile
    for i in range(SIZE):  # draws horizontal lines
        pygame.draw.line(win, GREY, [0, BLOCK_SIZE * i], [SIZE * BLOCK_SIZE, BLOCK_SIZE * i],
                         LINE_WIDTH)  # draws horizontal lines
        for j in range(SIZE):  # draws vertical lines
            pygame.draw.line(win, GREY, [BLOCK_SIZE * j, 0], [BLOCK_SIZE * j, SIZE * BLOCK_SIZE],
                             LINE_WIDTH)  # draw.line draws starting (x0, xf) (y0, yf)


def make_grid(size):  # creates the 2D array that stores all the values of tiles
    grid = [[0 for x in range(size)] for y in range(size)]  # creates 2d array
    nodes = size * size * [None]
    i = 0
    for x in range(size):
        for y in range(size):
            grid[x][y] = Tile(x, y)  # gives each Tile object a unique coordinate
            nodes[i] = grid[x][y]
            i += 1
    return grid


def give_neighbors(grid):  # adds neighbors to each tile but does not initialize
    size = len(grid)
    for y in range(size):
        for x in range(size):
            if x < size - 1:  # go to second to last tile because will make neighbor with last tile
                grid[x][y].add_neighbors(grid[x + 1][y])  # adds the neighbors right and down to both tiles
                grid[x][y].add_neighbors(grid[x][y - 1])
                if y == size - 1:  # at the last row just add neighbors to the right
                    grid[x][y].add_neighbors(grid[x + 1][y])


def dfs_block(list_in, x, y):  # method for initializing all blocks via dfs
    stack = []  # empty stack
    start = list_in[x][y]  # gets coordinate of starting node
    start.is_block = False
    start.initialize = True
    stack.append(start)
    while len(stack) != 0:
        n = stack.pop()  # pop the parent
        for t in n.neighbors:  # loop iterates for all children of parent
            if not t.initialize:
                t.initialize = True
                r = np.random.randint(0, 10)
                if r < 3:  # gives a 30% chance of being a block
                    t.is_block = True
                    t.color = BLACK
                stack.append(t)  # add neighbor to stack


def calc_f(tile: Tile, end):
    # print(tile.x, tile.y)
    tile.h = abs(end[0] - tile.x) + abs(end[1] - tile.y)
    # print(tile.h, tile.x, tile.y, end)
    tile.f = tile.h + tile.g


def a_star(start, end, grid):
    opened = []
    heapq.heapify(opened)
    index = 0
    # closed = BinaryHeap(100)
    s = grid[start[0]][start[1]]
    s.g = 0
    heapq.heappush(opened, (0, s))
    iteration = 0
    while True:
        iteration += 1
        current = heapq.heappop(opened)[1]
        index -= 1
        # print(current.parent)
        if (current is None):
            return
        current.color = "GREEN"
        current.closed = True

        if current.x == start[0] and current.y == start[1] and iteration != 1:
            for n in current.neighbors:
                if (n.g + 1 < current.g):
                    current.parent = n
            return

        if current.x == end[0] and current.y == end[1]:
            return opened
        # print(current.neighbors)
        for n in current.neighbors:
            if n.closed or n.is_block or n is None:
                continue
            n.g = current.g + 1
            print(n.g, current.g)
            if n.g > current.g or not n.closed:
                calc_f(n, end)
                n.parent = current

                if not n.closed:
                    index += 1

                    heapq.heappush(opened, (n.f, n))


def draw_path(start, end, grid):
    current: Tile = grid[end[0]][end[1]]
    while True:
        if current is None:
            return
        if (current == grid[start[0]][start[1]]):
            return
        current.color = "RED"
        current = current.parent
        # print(current.g, current.h)
        # print(current.neighbors)


def main():
    pygame.init()
    game_window = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("A* Path Finding Algo")

    my_grid = make_grid(SIZE)  # makes [100][100] and populates with tiles
    give_neighbors(my_grid)  # adds neighbors to tiles

    dfs_block(my_grid, 50, 50)  # makes tiles blocks or not blocks at starting block

    game_exit = False

    start = (int(random() * 100), int(random() * 100))
    end = (int(random() * 100), int(random() * 100))
    #    start = (50, 50)
    #    end = (51, 75)
    # print(start, end)

    a_star(start, end, my_grid)

    draw_path(start, end, my_grid)

    my_grid[start[0]][start[1]].color = "BLUE"
    my_grid[end[0]][end[1]].color = "BLUE"

    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
        draw_main(game_window, my_grid)  # draws the game window

    print("hello world")


if __name__ == "__main__":
    main()
