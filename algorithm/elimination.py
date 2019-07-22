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
        for i in range(81):
            if self.puzzle[i] == 0:
                self.possibilities.append([0, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            else:
                self.possibilities.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                self.possibilities[i][self.puzzle[i]] = 1
            # possible answer 0-9, 0 for impossible, 1 for possible

    def run(self):
        solution = self.solve_puzzle(self.puzzle)
        if solution:
            for i in range(9):
                print(solution[i*9 : i*9+9])
        print("done!")
        # self.puzzle_solved_signal.emit(solution)

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
                    reduction = self.reduce_possibilities(grid, i)
                    if reduction:
                        print("{} reduction result: {}, {}".format(i, reduction, self.possibilities[i]))
                        possibilities_updated = True
                    poss_value = 0
                    remaining = 0
                    for value in range(1, 10):
                        if self.possibilities[i][value] == 1:
                            poss_value = value
                            remaining += 1
                    print("{} remaining {}, {}".format(i, remaining, self.possibilities[i]))
                    if remaining == 0:
                        impossible_puzzle = True
                        print("{} remaining = 0, quit!".format(i))
                        break
                    elif remaining == 1:
                        grid[i] = poss_value
                        for index in range(9):
                            print(grid[index*9: index*9+9])
                        print("================== last possibility {} {}".format(i, poss_value))
                        possibilities_updated = True
                        continue
                    if freedomcheck_needed:
                        solution = self.check_freedoms(self.possibilities, i)
                        if len(solution) == 1:
                            for index in range(9):
                                print(grid[index * 9: index * 9 + 9])
                            print("====================== found {} solution {} by freedom check!".format(i, solution[0]))
                            grid[i] = solution[0]
                            possibilities_updated = True
                            continue
                        if remaining == least_remaining:
                            least_free_indexes.append(i)
                        elif remaining < least_remaining:
                            least_free_indexes = [i]
                            least_remaining = remaining
                            print("{} possibility remaining = {}".format(i, remaining))
            if impossible_puzzle:
                print("impossible puzzle")
                break
            elif not (possibilities_updated or puzzle_solved):
                if freedomcheck_needed:
                    return self.solve_by_guessing(grid, least_free_indexes)
                else:
                    freedomcheck_needed = True
            print("round {}, update={}, solved={}, impossible={}".format(i, possibilities_updated, puzzle_solved, impossible_puzzle))
        if impossible_puzzle:
            return None
        else:
            return grid

    def solve_by_guessing(self, puzzle, least_free_indexes):
        grid = puzzle.copy()
        # guess_index = choice(least_free_indexes)
        guess_index = least_free_indexes[0]
        guess_values = []
        print("least free indexes: {}".format(least_free_indexes))
        print("guess index: {}, {}".format(guess_index, self.possibilities[guess_index]))
        for value in range(1, 10):
            if self.possibilities[guess_index][value]:
                guess_values.append(value)
        for value in guess_values:
            print("solve puzzle by guessing {}, {}".format(guess_index, value))
            grid[guess_index] = value
            result = self.solve_puzzle(grid)
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
                    # print("value: {}, last_value: {}".format(value, last_value))
        return last_value

    def reduce_possibilities(self, puzzle, i):
        row, col, square = get_related_grids(puzzle, i)
        result = False
        for value in range(1, 10):
            if self.possibilities[i][value] and value in (row + col + square):
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
