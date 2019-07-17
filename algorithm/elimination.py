from PyQt5.QtCore import QThread, pyqtSignal
from random import choice
import logging


logger = logging.getLogger(__name__)


class Solver(QThread):
    puzzle_solved_signal = pyqtSignal(list)
    possibilities = []
    puzzle = []

    def __init__(self):
        super(Solver, self).__init__()

    def set_puzzle(self, puzzle):
        self.puzzle = puzzle
        poss = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # possible answer 0-9, 0 for impossible, 1 for possible
        for i in range(81):
            self.possibilities.append(poss)

    def run(self):
        solution = self.solve_puzzle(self.puzzle)
        self.puzzle_solved_signal.emit(solution)

    def solve_puzzle(self, puzzle):
        grid = puzzle.copy()
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
                    if self.reduce_possibilities(grid, i):
                        possibilities_updated = True
                    poss_value = 0
                    remaining = 0
                    for value in range(1, 10):
                        if self.possibilities[i][value] == 1:
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
                        solution = self.check_freedoms(self.possibilities, i)
                        if solution:
                            print("found solution by freedom check!")
                            grid[i] = solution
                            possibilities_updated = True
                            continue
                        if remaining == least_remaining:
                            least_free_indexes.append(i)
                        elif remaining < least_remaining:
                            least_free_indexes = [i]
            if impossible_puzzle:
                break
            elif not (possibilities_updated or puzzle_solved):
                if freedomcheck_needed:
                    return self.solve_by_guessing(grid, least_free_indexes)
                else:
                    freedomcheck_needed = True
        if impossible_puzzle:
            return None
        else:
            return grid

    def solve_by_guessing(self, puzzle, least_free_indexes):
        grid = puzzle.copy()
        guess_index = choice(least_free_indexes)
        guess_values = []
        for value in range(1, 10):
            if self.possibilities[guess_index][value]:
                guess_values.append(value)
        for value in guess_values:
            grid[guess_index] = value
            result = self.solve_puzzle(grid)
            if result:
                return result
        return None

    def check_freedoms(self, possibilities, i):
        result = 0
        row_poss, col_poss, square_poss = get_related_grids(possibilities, i)
        for group in [row_poss, col_poss, square_poss]:
            last_value = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for grid in group:
                for value in range(1, 10):
                    if possibilities[i][value] and grid[value]:
                        last_value.remove(value)
                if len(last_value) == 1:
                    result = last_value
                    return result
        return result

    def reduce_possibilities(self, puzzle, i):
        row, col, square = get_related_grids(puzzle, i)
        result = False
        for value in range(1, 10):
            if value in (row + col + square):
                self.possibilities[i][value] = 0
                result = True
        return result

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
