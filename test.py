from __future__ import division
import numpy as np
import random
import math

def set_percentage(percentage, grid, to):
    if type(grid) is list and type(to) is list:
        size = len(grid[0]) * len(grid[0][0])
        len_cells = int(math.ceil(size * percentage))

        for i in range(0, len_cells):
            index = random.randrange(size)
            x, y = np.unravel_index(index, (len(grid[0]), len(grid[0][0])))
            while grid[0][x][y] != 0:
                index = random.randrange(size)
                x, y = np.unravel_index(index, (len(grid[0]), len(grid[0][0])))
            for i, g in enumerate(grid):
                g[x][y] = to[i]
    else:
        size = len(grid) * len(grid[0])
        len_cells = int(math.ceil(size * percentage))

        for i in range(0, len_cells):
            index = random.randrange(size)
            x, y = np.unravel_index(index, (len(grid), len(grid[0])))
            while grid[x][y] != 0:
                index = random.randrange(size)
                x, y = np.unravel_index(index, (len(grid), len(grid[0])))
            grid[x][y] = to


test = np.zeros((10, 10))
test2 = np.zeros((100, 100))

# print test
set_percentage(0.4, [test, test2], [1, 14])

print test
print test2
