from PyQt5.QtCore import QThread, pyqtSignal
from random import choice, shuffle
import logging


logger = logging.getLogger(__name__)
INDEX_LIST = list(i for i in range(0, 81))


class Generator(QThread):
    new_puzzle_generated_signal = pyqtSignal(list, list)

    def __init__(self):
        super(Generator, self).__init__()
        self.puzzle_solver = Solver()

    def run(self):
        logger.info("generating new puzzle..")
        full_puzzle = self.init_grid()
        logger.info("create puzzle from full grid:")
        for i in range(9):
            logger.info(full_puzzle[i * 9:i * 9 + 9])
        possibilities = []
        for i in range(81):
            poss = [0]*10
            poss[full_puzzle[i]] = 1
            possibilities.append(poss)
        puzzle = self.create_puzzle(full_puzzle, possibilities)
        logger.info("puzzle created:")
        for i in range(9):
            logger.info(puzzle[i * 9:i * 9 + 9])
        self.new_puzzle_generated_signal.emit(puzzle, full_puzzle)

    def init_grid(self):
        empty_grid = [0]*81
        empty_poss_grid = []
        for i in range(81):
            empty_poss_grid.append([0, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        full_puzzle = self.puzzle_solver.solve_puzzle(empty_grid, empty_poss_grid)
        return full_puzzle

    def create_puzzle(self, puzzle, poss):
        current_puzzle = puzzle.copy()
        possibilities = poss.copy()
        shuffle(INDEX_LIST)
        for index in INDEX_LIST:
            if current_puzzle[index] != 0:
                current_value = current_puzzle[index]
                current_puzzle[index] = 0
                possibilities[index] = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                possibilities[index][current_value] = 0
                result = self.puzzle_solver.solve_puzzle(current_puzzle, possibilities)
                if result:
                    # logger.info("{} = {} cannot remove".format(index, current_value))
                    current_puzzle[index] = current_value
                    possibilities[index] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    possibilities[index][current_value] = 1
                else:
                    # logger.info("remove {} = {}".format(index, current_value))
                    possibilities[index][current_value] = 1
                    # for i in range(9):
                    #     logger.info(current_puzzle[i*9:i*9+9])
        return current_puzzle


class Solver(QThread):
    puzzle_solved_signal = pyqtSignal(list)
    possibilities = []
    puzzle = []

    def __init__(self):
        super(Solver, self).__init__()

    def set_puzzle(self, puzzle):
        self.puzzle = puzzle
        for i in range(81):
            if self.puzzle[i] == 0:
                self.possibilities.append([0, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            else:
                self.possibilities.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                self.possibilities[i][self.puzzle[i]] = 1
            # possible answer 0-9, 0 for impossible, 1 for possible

    def run(self):
        solution = self.solve_puzzle(self.puzzle, self.possibilities)
        if solution:
            logger.info("Sudoku solved:")
            for i in range(9):
                logger.info(solution[i*9 : i*9+9])
        self.puzzle_solved_signal.emit(solution)

    def solve_puzzle(self, puzzle, poss_grid):
        grid = puzzle.copy()
        possibilities = poss_grid.copy()
        puzzle_solved = False
        impossible_puzzle = False
        freedomcheck_needed = False
        while not (puzzle_solved or impossible_puzzle):
            puzzle_solved = True
            possibilities_updated = False
            least_free_indexes = []
            least_remaining = 9

            for i in range(81):
                if grid[i] == 0:
                    puzzle_solved = False
                    reduction, result = self.reduce_possibilities(grid, i, possibilities[i])
                    if reduction:
                        possibilities[i] = result
                        possibilities_updated = True
                    poss_value = 0
                    remaining = 0
                    for value in range(1, 10):
                        if possibilities[i][value] == 1:
                            poss_value = value
                            remaining += 1
                    if remaining == 0:
                        impossible_puzzle = True
                        break
                    elif remaining == 1:
                        grid[i] = poss_value
                        possibilities_updated = True
                        continue
                    if freedomcheck_needed:
                        solution = self.check_freedoms(possibilities, i)
                        if len(solution) == 1:
                            grid[i] = solution[0]
                            possibilities_updated = True
                            continue
                        if remaining == least_remaining:
                            least_free_indexes.append(i)
                        elif remaining < least_remaining:
                            least_free_indexes = [i]
                            least_remaining = remaining
            if impossible_puzzle:
                # logger.info("impossible puzzle")
                break
            elif not (possibilities_updated or puzzle_solved):
                if freedomcheck_needed:
                    return self.solve_by_guessing(grid, least_free_indexes, possibilities)
                else:
                    freedomcheck_needed = True
        if impossible_puzzle:
            return None
        else:
            return grid

    def solve_by_guessing(self, puzzle, least_free_indexes, poss_grid):
        grid = puzzle.copy()
        possibilities = poss_grid.copy()
        guess_index = choice(least_free_indexes)
        guess_values = []
        for value in range(1, 10):
            if possibilities[guess_index][value]:
                guess_values.append(value)
        for value in guess_values:
            # logger.info("solve puzzle by guessing {}, {}".format(guess_index, value))
            grid[guess_index] = value
            result = self.solve_puzzle(grid, possibilities)
            if result:
                return result
        return None

    def check_freedoms(self, possibilities, i):
        row_poss, col_poss, square_poss = get_related_grids(possibilities, i)
        last_value = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for grid in (row_poss + col_poss + square_poss):
            for value in range(1, 10):
                if grid[value] and (value in last_value):
                    last_value.remove(value)
        return last_value

    def reduce_possibilities(self, puzzle, i, poss_grid):
        possibilities = poss_grid.copy()
        row, col, square = get_related_grids(puzzle, i)
        updated = False
        for value in range(1, 10):
            if possibilities[value] and value in (row + col + square):
                possibilities[value] = 0
                updated = True
        return updated, possibilities

def get_related_grids(puzzle, i):
    grid = puzzle.copy()
    row = i // 9
    col = i % 9
    row_item = grid[9 * row: 9 * (row + 1)]
    col_item = [grid[col], grid[9 + col], grid[2 * 9 + col], grid[3 * 9 + col], grid[4 * 9 + col],
                grid[5 * 9 + col], grid[6 * 9 + col], grid[7 * 9 + col], grid[8 * 9 + col]]
    x = (row // 3) * 3 * 9 + (col // 3) * 3  # first item in the square
    square_item = grid[x:x+3] + grid[x+9: x+12] + grid[x+18:x+21]
    del row_item[col]
    del col_item[row]
    del square_item[row % 3 * 3 + col % 3]   # remove the target grid
    return row_item, col_item, square_item
