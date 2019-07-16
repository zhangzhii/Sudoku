from PyQt5.QtCore import QThread, pyqtSignal
from random import shuffle
import logging


NUMBER_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]
INDEX_LIST = list(i for i in range(0, 81))
logger = logging.getLogger(__name__)


class Generator(QThread):
    new_puzzle_generated_signal = pyqtSignal(list, list)
    solve_tracking_index = []
    solve_tracking_value = []
    fill_tracking_index = []
    fill_tracking_value = []
    remove_tracking_index = []
    remove_tracking_value = []

    def __init__(self):
        super(Generator, self).__init__()

    def run(self):
        self.fill_tracking_index.clear()
        self.fill_tracking_value.clear()
        new_grid = [0] * 81
        while True:
            new_grid = self.fill_grid(new_grid)
            if check_grid(new_grid):
                break
        logger.info("full grid created:")
        for i in range(9):
            logger.info(str(new_grid[9 * i:9 * i + 9]))
        self.create_puzzle(new_grid)

    def fill_grid(self, grid):
        numbers = grid
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if numbers[i] == 0:
                if i not in self.fill_tracking_index:
                    self.fill_tracking_index.append(i)
                    self.fill_tracking_value.append([])
                shuffle(NUMBER_LIST)
                for value in NUMBER_LIST:
                    if i == self.fill_tracking_index[-1] and self.fill_tracking_value[-1] != [] and \
                            value in self.fill_tracking_value[-1]:
                        continue
                    self.fill_tracking_value[-1].append(value)
                    if value not in numbers[9*row : 9*row+9]:
                        col_nums = [numbers[col], numbers[9+col], numbers[2*9+col], numbers[3*9+col], numbers[4*9+col],
                                    numbers[5*9+col], numbers[6*9+col], numbers[7*9+col], numbers[8*9+col]]
                        if value not in col_nums:
                            x = (row // 3) * 3 * 9 + (col // 3) * 3  # first item in the square
                            square_item = [numbers[x], numbers[x + 1], numbers[x + 2],
                                           numbers[x + 9], numbers[x + 10], numbers[x + 11],
                                           numbers[x + 18], numbers[x + 19], numbers[x + 20]]
                            if value not in square_item:
                                numbers[i] = value
                                return numbers
                break
        del self.fill_tracking_index[-1]
        del self.fill_tracking_value[-1]
        numbers[self.fill_tracking_index[-1]] = 0
        return numbers

    def create_puzzle(self, full_grid):
        numbers = full_grid
        self.remove_tracking_index.clear()
        self.remove_tracking_value.clear()
        shuffle(INDEX_LIST)
        for i in INDEX_LIST:
            if numbers[i] != 0:
                self.remove_tracking_index.append(i)
                self.remove_tracking_value.append(numbers[i])
                self.solve_tracking_index.clear()
                self.solve_tracking_value.clear()
                numbers[i] = 0
                grid_for_validate = numbers.copy()
                while True:
                    grid_for_validate = self.validate_grid(grid_for_validate)
                    if grid_for_validate == True:
                        break
                    elif check_grid(grid_for_validate):
                        numbers[i] = self.remove_tracking_value[-1]
                        break
        logger.info("new puzzle created! ")
        self.new_puzzle_generated_signal.emit(numbers, full_grid)
        for i in range(9):
            logger.info(str(numbers[i*9: i*9+9]))

    def validate_grid(self, grid):
        numbers = grid
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if numbers[i] == 0:
                if i not in self.solve_tracking_index:
                    self.solve_tracking_index.append(i)
                    self.solve_tracking_value.append(0)
                for value in range(1, 10):
                    if i == self.remove_tracking_index[-1] and value == self.remove_tracking_value[-1]:
                        continue
                    if i == self.solve_tracking_index[-1] and value <= self.solve_tracking_value[-1]:
                        continue
                    self.solve_tracking_value[-1] = value
                    if value not in numbers[9 * row: 9 * (row + 1)]:
                        col_items = [numbers[col], numbers[9 + col], numbers[2 * 9 + col], numbers[3 * 9 + col],
                                     numbers[4 * 9 + col],
                                     numbers[5 * 9 + col], numbers[6 * 9 + col], numbers[7 * 9 + col],
                                     numbers[8 * 9 + col]]
                        if value not in col_items:
                            x = (row // 3) * 3 * 9 + (col // 3) * 3  # first item in the square
                            square_item = [numbers[x], numbers[x + 1], numbers[x + 2],
                                           numbers[x + 9], numbers[x + 10], numbers[x + 11],
                                           numbers[x + 18], numbers[x + 19], numbers[x + 20]]
                            if value not in square_item:
                                numbers[i] = value
                                return numbers
                break  # not valid for all 9 values
        del self.solve_tracking_index[-1]
        del self.solve_tracking_value[-1]
        if self.solve_tracking_index == []:
            return True
        else:
            numbers[self.solve_tracking_index[-1]] = 0
            return numbers


class Solver(QThread):
    puzzle_solved_signal = pyqtSignal(list)
    solve_tracking_index = []
    solve_tracking_value = []
    grid = []

    def __init__(self):
        super(Solver, self).__init__()

    def set_puzzle(self, puzzle):
        self.grid = puzzle

    def run(self):
        logger.info("start solving...")
        self.solve_tracking_index.clear()
        self.solve_tracking_value.clear()
        numbers = self.grid.copy()
        while True:
            numbers = self.solve_grid(numbers)
            if check_grid(numbers):
                break
        logger.info("solved:")
        self.puzzle_solved_signal.emit(numbers)
        for i in range(9):
            logger.info(str(numbers[9 * i:9 * i + 9]))

    def solve_grid(self, grid):
        numbers = grid
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if numbers[i] == 0:
                if i not in self.solve_tracking_index:
                    self.solve_tracking_index.append(i)
                    self.solve_tracking_value.append(0)
                for value in range(1, 10):
                    if i == self.solve_tracking_index[-1] and value <= self.solve_tracking_value[-1]:
                        continue
                    self.solve_tracking_value[-1] = value
                    if value not in numbers[9*row : 9*(row+1)]:
                        col_items = [numbers[col], numbers[9+col], numbers[2*9+col], numbers[3*9+col], numbers[4*9+col],
                                     numbers[5*9+col], numbers[6*9+col], numbers[7*9+col], numbers[8*9+col]]
                        if value not in col_items:
                            x = (row//3)*3*9 + (col//3)*3  # first item in the square
                            square_item = [numbers[x], numbers[x+1], numbers[x+2],
                                           numbers[x+9], numbers[x+10], numbers[x+11],
                                           numbers[x+18], numbers[x+19], numbers[x+20]]
                            if value not in square_item:
                                numbers[i] = value
                                return numbers
                break  # not valid for all 9 values
        del self.solve_tracking_index[-1]
        del self.solve_tracking_value[-1]
        numbers[self.solve_tracking_index[-1]] = 0
        return numbers


def check_grid(grid):
    if 0 in grid:
        return False
    else:
        return True
