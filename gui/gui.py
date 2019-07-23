from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from gui.sudoku_grid import Ui_MainWindow
# from algorithm.brute_force import Generator
from algorithm.elimination import Solver, Generator
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
DEBUG_MODE = False
logger = logging.getLogger(__name__)


class SudokuMaster(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SudokuMaster, self).__init__()
        self.setupUi(self)
        self.generator = Generator()
        self.generator.new_puzzle_generated_signal.connect(self.onPuzzleCreated)
        self.solver = Solver()
        self.solver.puzzle_solved_signal.connect(self.onPuzzleSolved)
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
        self.generator.start()
        for widget in self.grid:
            widget.clear()
            widget.setEnabled(True)

    def onClickedConfirmButton(self):
        logger.info("start solving puzzle...")
        puzzle = []
        if DEBUG_MODE:
            for i in range(81):
                if TEST_GRID[i] != 0:
                    self.grid[i].setText(str(TEST_GRID[i]))
                    self.grid[i].setEnabled(False)
                    puzzle.append(TEST_GRID[i])
                else:
                    puzzle.append(0)
        else:
            for widget in self.grid:
                if widget.text() == "":
                    puzzle.append(0)
                else:
                    puzzle.append(int(widget.text()))
        self.solver.set_puzzle(puzzle)
        self.solver.start()

    def onPuzzleSolved(self, answer):
        if answer:
            for i in range(81):
                self.grid[i].setText(str(answer[i]))
        else:
            logger.info("impossible puzzle!")

    def onPuzzleCreated(self, puzzle, answer):
        for i in range(81):
            if puzzle[i] != 0:
                self.grid[i].setText(str(puzzle[i]))
                self.grid[i].setEnabled(False)


def custom_sort(t):
    return int(str(t.objectName())[4:])


