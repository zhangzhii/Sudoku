from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
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

logger = logging.getLogger(__name__)
DEBUG_MODE = True


class SudokuMaster(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SudokuMaster, self).__init__()
        self.setupUi(self)
        self.grid = []
        self.tracking_index = []
        self.tracking_value = []
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

    def onClickedResetButton(self):
        for widget in self.grid:
            widget.clear()
            widget.setEnabled(True)

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

    def solve_grid(self, grid):
        numbers = grid
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if numbers[i] == 0:
                if i not in self.tracking_index:
                    self.tracking_index.append(i)
                    self.tracking_value.append(0)
                for value in range(1, 10):
                    if i == self.tracking_index[-1] and value <= self.tracking_value[-1]:
                        continue
                    self.tracking_value[-1] = value
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
        del self.tracking_index[-1]
        del self.tracking_value[-1]
        numbers[self.tracking_index[-1]] = 0
        return numbers

    def check_grid(self, grid):
        if 0 in grid:
            return False
        else:
            logger.info("done!")
            return True

def custom_sort(t):
    return int(str(t.objectName())[4:])


