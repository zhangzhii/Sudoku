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
        for widget in self.grid:
            if widget.text() != "":
                widget.setEnabled(False)


def custom_sort(t):
    return int(str(t.objectName())[4:])


