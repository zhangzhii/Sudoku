from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from random import shuffle
from gui.sudoku_grid import Ui_MainWindow
import logging


TEST_GRID = [3, 0, 6,   5, 0, 8,   4, 0, 0,
             5, 2, 0,   0, 0, 0,   0, 0, 0,
             0, 8, 7,   0, 0, 0,   0, 3, 1,

             0, 0, 3,   0, 1, 0,   0, 8, 0,
             9, 0, 0,   8, 6, 3,   0, 0, 5,
             0, 5, 0,   0, 9, 0,   6, 0, 0,

             1, 3, 0,   0, 0, 0,   2, 5, 0,
             0, 0, 0,   0, 0, 0,   0, 7, 4,
             0, 0, 5,   2, 0, 6,   3, 0, 0]
NUMBER_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]
INDEX_LIST = list(i for i in range(0, 81))
logger = logging.getLogger(__name__)
DEBUG_MODE = True


class SudokuMaster(QMainWindow, Ui_MainWindow):
    solve_tracking_index = []
    solve_tracking_value = []
    fill_tracking_index = []
    fill_tracking_value = []
    remove_tracking_index = []
    remove_tracking_value = []

    def __init__(self):
        super(SudokuMaster, self).__init__()
        self.setupUi(self)
        self.grid = []
        self.initUi()

    def initUi(self):
        validator = QRegExpValidator(QRegExp("^[1-9]$"))
        for widget in self.centralwidget.children():
            if isinstance(widget, QLineEdit):
                widget.setValidator(validator)
                self.grid.append(widget)
        self.grid.sort(key=custom_sort)  # reorder the list by widget name
        self.confirm_Button.clicked.connect(self.onClickedConfirmButton)
        self.reset_Button.clicked.connect(self.onClickedResetButton)
        self.new_Button.clicked.connect(self.onClickedNewGameButton)

    def onClickedResetButton(self):
        logger.info("clear ~")
        for widget in self.grid:
            if widget.isEnabled():
                widget.clear()

    def onClickedNewGameButton(self):
        self.fill_tracking_index.clear()
        self.fill_tracking_value.clear()
        for widget in self.grid:
            widget.clear()
            widget.setEnabled(True)
        new_grid = [0]*81
        while True:
            new_grid = self.fill_grid(new_grid)
            if self.check_grid(new_grid):
                break
        for i in range(81):
            self.grid[i].setText(str(new_grid[i]))
        logger.info("full grid created:")
        for i in range(9):
            logger.info(str(new_grid[9*i:9*i+9]))
        self.create_puzzle(new_grid)

    def onClickedConfirmButton(self):
        logger.info("start solving...")
        if DEBUG_MODE:
            numbers = TEST_GRID
            for i in range(81):
                if numbers[i] != 0:
                    self.grid[i].setText(str(numbers[i]))
                    self.grid[i].setEnabled(False)
        else:
            numbers = []
            for widget in self.grid:
                if widget.text() != "":
                    widget.setEnabled(False)
                    numbers.append(int(widget.text()))
                else:
                    numbers.append(0)
        while True:
            numbers = self.solve_grid(numbers)
            if self.check_grid(numbers):
                break
        logger.info("solved:")
        for i in range(9):
            logger.info(str(numbers[9 * i:9 * i + 9]))

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

    def create_puzzle(self, grid):
        numbers = grid
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
                for j in range(9):
                    print(numbers[j * 9: j * 9 + 9])
                print("============================= ", i, len(self.remove_tracking_index))
                grid_for_validate = numbers.copy()
                while True:
                    grid_for_validate = self.validate_grid(grid_for_validate)
                    if grid_for_validate == True:
                        break
                    elif self.check_grid(grid_for_validate):
                        numbers[i] = self.remove_tracking_value[-1]
                        print("not allow ", i, self.remove_tracking_value[-1])
                        break
        print("new puzzle created! ")
        for i in range(9):
            print(numbers[i*9: i*9+9])

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
                                self.grid[i].setText(str(value))
                                return numbers
                break  # not valid for all 9 values
        del self.solve_tracking_index[-1]
        del self.solve_tracking_value[-1]
        if self.solve_tracking_index == []:
            return True
        else:
            numbers[self.solve_tracking_index[-1]] = 0
            return numbers

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
                                self.grid[i].setText(str(value))
                                return numbers
                break  # not valid for all 9 values
        del self.solve_tracking_index[-1]
        del self.solve_tracking_value[-1]
        numbers[self.solve_tracking_index[-1]] = 0
        return numbers

    def check_grid(self, grid):
        if 0 in grid:
            return False
        else:
            return True


def custom_sort(t):
    return int(str(t.objectName())[4:])


