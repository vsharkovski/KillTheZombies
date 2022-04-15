import copy
import json
import os
import random
from collections import deque

from Config import config
from Pair import Pair
from Sprite import Sprite


class Map:
    def __init__(self, decorationSprites):
        self.X = config.GRID_COLS
        self.Y = config.GRID_ROWS
        self.decorationSprites = decorationSprites
        self.lastSource = None

        noneGrid = []
        for x in range(self.X):
            noneGrid.append([])
            for y in range(self.Y):
                noneGrid[x].append(None)

        self.grid = copy.deepcopy(noneGrid)
        self.colorGrid = copy.deepcopy(noneGrid)
        self.decorationGrid = copy.deepcopy(noneGrid)
        self.bfsDistance = copy.deepcopy(noneGrid)
        self.eData = copy.deepcopy(noneGrid)

        for x in range(self.X):
            for y in range(self.Y):
                self.grid[x][y] = config.CELL_NONE
        
        self.structures = []
        for structureData in config.STRUCTURES:
            structure = Structure(structureData)
            for _ in range(4):
                self.structures.append(copy.deepcopy(structure))
                structure.rotate()


    def generate_walls(self):
        for x in range(self.X):
            for y in range(self.Y):
                self.grid[x][y] = config.CELL_EMPTY

        for x in range(self.X):
            self.grid[x][0] = config.CELL_WALL
            self.grid[x][self.Y-1] = config.CELL_WALL
        
        for y in range(self.Y):
            self.grid[0][y] = config.CELL_WALL
            self.grid[self.X-1][y] = config.CELL_WALL

        numStructures = random.randint(5, 15)
        for _ in range(numStructures):
            options = []
            prefixSumDS = PrefixSumDataStructure(self.grid)

            for structure in self.structures:
                possiblePositions = self.get_possible_structure_positions(structure, prefixSumDS)
                if len(possiblePositions) > 0:
                    options.append((structure, possiblePositions))
            
            if len(options) == 0:
                # can't place anything anymore
                break

            structure, positions = random.choice(options)
            cell = random.choice(positions)
            
            # print("Placing {} at {}".format(structure, cell))
            
            # place the structure
            for x in range(cell.x, cell.x + structure.X):
                for y in range(cell.y, cell.y + structure.Y):
                    self.grid[x][y] = structure.grid[x - cell.x][y - cell.y]

        self.remove_walls_so_grid_is_connected()

        # add colors to cells
        for x in range(self.X):
            for y in range(self.Y):
                if self.grid[x][y] == config.CELL_WALL:
                    self.colorGrid[x][y] = random.choice(config.WALL_COLORS)
                else:
                    self.colorGrid[x][y] = random.choice(config.FLOOR_COLORS)
        
        # ensure next bfs is run
        self.lastSource = None


    def generate_decorations(self):
        """
        Turn some empty cells in grid to decoration cells.
        """
        if len(self.decorationSprites) == 0:
            return
        
        emptyCells = []
        for x in range(self.X):
            for y in range(self.Y):
                self.decorationGrid[x][y] = None
                if self.grid[x][y] == config.CELL_EMPTY:
                    emptyCells.append(Pair(x, y))
        
        numDecorations = min(len(emptyCells), random.randint(
            floor(0.01 * (config.GRID_COLS*config.GRID_ROWS)),
            floor(0.03 * (config.GRID_COLS*config.GRID_ROWS))
        ))

        cells = random.sample(emptyCells, numDecorations)
        for cell in cells:
            self.grid[cell.x][cell.y] = config.CELL_DECO
            self.decorationGrid[cell.x][cell.y] = random.choice(self.decorationSprites)


    def get_random_cell(self, cellValue):
        """
        Return a random cell from grid such that it has
        value cellValue, or None if there are none.
        """
        result = []
        for x in range(self.X):
            for y in range(self.Y):
                if self.grid[x][y] == cellValue:
                    result.append(Pair(x, y))
        
        return None if len(result) == 0 else random.choice(result)


    def get_possible_structure_positions(self, structure, prefixSumDS, dbg=False):
        # terrible time complexity, but doesn't matter
        result = []

        for x1 in range(0, self.X):
            x2 = x1 + structure.X - 1
            
            for y1 in range(0, self.Y):
                y2 = y1 + structure.Y - 1
                if x2 >= self.X or y2 >= self.Y:
                    break
                
                if prefixSumDS.sum2d(x1, y1, x2, y2) == 0:
                    result.append(Pair(x1, y1))

        return result


    def remove_walls_so_grid_is_connected(self):
        dsu = DisjointSetDataStructure(self.X * self.Y)

        # connect all connected components of empty cells
        for x in range(0, self.X-1):
            for y in range(0, self.Y-1):
                if self.grid[x][y] == config.CELL_WALL:
                    continue

                deltas = [(1, 0), (0, 1)]
                for dx, dy in deltas:
                    x1, y1 = x + dx, y + dy
                    if self.grid[x1][y1] == config.CELL_WALL:
                        continue

                    # print("Joining {} and {}".format(Pair(x, y), Pair(x1, y1)))
                    dsu.join(x*self.Y + y, x1*self.Y + y1)

        # remove walls to connect different connected components
        for x in range(0, self.X):
            for y in range(0, self.Y):
                if self.grid[x][y] != config.CELL_WALL:
                    continue
                
                adjacentEmptyNum = None
                connectedTwo = False

                deltas = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for dx, dy in deltas:
                    x1, y1 = x + dx, y + dy
                    if (
                        not self.cell_inside_grid(Pair(x1, y1))
                        or self.grid[x1][y1] == config.CELL_WALL
                    ):
                        continue
                    
                    hereNum = x1*self.Y + y1
                    if adjacentEmptyNum is None:
                        adjacentEmptyNum = hereNum
                    elif dsu.get(adjacentEmptyNum) != dsu.get(hereNum):
                        dsu.join(hereNum, adjacentEmptyNum)
                        connectedTwo = True
                
                if connectedTwo:
                    # connected, so make this empty too
                    self.grid[x][y] = config.CELL_EMPTY
                    dsu.join(x*self.Y + y, adjacentEmptyNum)


    def run_bfs(self, source):
        if self.lastSource is not None:
            if self.lastSource.x == source.x and self.lastSource.y == source.y:
                # No need to run it again
                return
        
        # print("Running bfs {}".format(source))
        self.lastSource = Pair(source.x, source.y)

        deltas = [Pair(-1, 0), Pair(1, 0), Pair(0, -1), Pair(0, 1)]
        for x in range(self.X):
            for y in range(self.Y):
                self.bfsDistance[x][y] = None

        if self.grid[source.x][source.y] == config.CELL_WALL:
            return

        queue = deque()
        queue.append(source)
        self.bfsDistance[source.x][source.y] = 0

        while len(queue) > 0:
            topCell = queue.popleft()
            for delta in deltas:
                nextCell = topCell + delta
                if (
                    self.cell_inside_grid(nextCell)
                    and self.grid[nextCell.x][nextCell.y] != config.CELL_WALL
                ):
                    if self.bfsDistance[nextCell.x][nextCell.y] == None:
                        self.bfsDistance[nextCell.x][nextCell.y] = self.bfsDistance[topCell.x][topCell.y] + 1
                        queue.append(nextCell)


    def cell_inside_grid(self, cell):
        return 0 <= cell.x < self.X and 0 <= cell.y < self.Y



class Structure:
    def __init__(self, source):
        """
        source: a non-empty list of equal-length strings representing the structure,
        with 0=empty and 1=wall
        """
        self.X = len(source)
        self.Y = len(source[0])
        self.grid = []
        for x in range(self.X):
            self.grid.append([])
            for y in range(self.Y):
                self.grid[x].append(config.STRUCTURE_SYMBOLS[source[x][y]])
        
        self.rotationNumber = 0
        self.rotations = [(self.X, self.Y, self.grid), None, None, None]


    def rotate(self):
        """Rotate the grid 90 degrees clockwise. Update X and Y accordingly."""
        self.rotationNumber = (self.rotationNumber + 1) % 4
        
        if self.rotations[self.rotationNumber] is None:
            newGrid = []
            for y in range(self.Y):
                newGrid.append([])
                for x in range(self.X):
                    newGrid[y].append(None)
            
            for x in range(self.X):
                for y in range(self.Y):
                    newGrid[y][self.X - x - 1] = self.grid[x][y]

            self.rotations[self.rotationNumber] = (self.Y, self.X, newGrid)
        
        self.X, self.Y, self.grid = self.rotations[self.rotationNumber]


    def __repr__(self):
        s = "<Structure "
        for x in range(self.X):
            for y in range(self.Y):
                s += str(self.grid[x][y])
            s += " "
        s += ">"
        return s



class PrefixSumDataStructure:
    def __init__(self, grid):
        self.X = len(grid)
        self.Y = len(grid[0])
        self.grid = []
        for x in range(self.X):
            self.grid.append([])
            for y in range(self.Y):
                self.grid[x].append(1 if grid[x][y] == config.CELL_WALL else 0)
                if x > 0:
                    self.grid[x][y] += self.grid[x-1][y]
                if y > 0:
                    self.grid[x][y] += self.grid[x][y-1]
                if x > 0 and y > 0:
                    self.grid[x][y] -= self.grid[x-1][y-1]


    def sum2d(self, x1, y1, x2, y2):
        if x2 < x1 or y2 < y1:
            return 0
        
        result = self.grid[x2][y2]
        if x1 > 0:
            result -= self.grid[x1-1][y2]
        if y1 > 0:
            result -= self.grid[x2][y1-1]
        if x1 > 0 and y1 > 0:
            result += self.grid[x1-1][y1-1]
        
        return result



class DisjointSetDataStructure:
    def __init__(self, n):
        self.n = n
        self.parent = [i for i in range(n)]
        self.rank = [0 for i in range(n)]


    def get(self, u):
        if self.parent[u] == u:
            return u

        self.parent[u] = self.get(self.parent[u])
        return self.parent[u]


    def join(self, u, v):
        u, v = self.get(u), self.get(v)
        if u == v:
            return
        
        if self.rank[u] < self.rank[v]:
            u, v = v, u

        if self.rank[u] == self.rank[v]:
            self.rank[u] += 1

        self.parent[v] = u



def print_grid(grid):
    X = len(grid)
    Y = len(grid[0])
    for x in range(X):
        s = ""
        for y in range(Y):
            t = str(grid[x][y])
            while len(t) < 2:
                t = " " + t
            s += t + " "
        print(s)
