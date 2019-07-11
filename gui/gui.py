from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from gui.sudoku_grid import Ui_MainWindow


class SudokuMaster(QMainWindow, Ui_MainWindow):
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

    def onClickedResetButton(self):
        for widget in self.grid:
            widget.clear()
            widget.setEnabled(True)

    def onClickedConfirmButton(self):
        numbers = []
        for widget in self.grid:
            if widget.text() != "":
                widget.setEnabled(False)
                numbers.append(int(widget.text()))
            else:
                numbers.append(0)
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if numbers[i] == 0:
                for value in range(1, 10):
                    if value not in numbers[9*row : 9*(row+1)]:
                        col_items = [numbers[col], numbers[9+col], numbers[2*9+col], numbers[3*9+col], numbers[4*9+col],
                                     numbers[5*9+col], numbers[6*9+col], numbers[7*9+col], numbers[8*9+col]]
                        if value not in col_items:
                            x = row*3*9 + col*3  # first item in the square
                            square_item = [numbers[x], numbers[x+1], numbers[x+2],
                                           numbers[x+9], numbers[x+10], numbers[x+11],
                                           numbers[x+18], numbers[x+19], numbers[x+20]]
                            if value not in square_item:
                                numbers[i] = value
                                self.grid[i].setText(value)



def custom_sort(t):
    return int(str(t.objectName())[4:])


