import sys
import logging
from gui import gui
from PyQt5.QtWidgets import QApplication
import utility.log as log

if __name__ == "__main__":
    log.setup_logging()
    logger = logging.getLogger(__name__)
    app = QApplication(sys.argv)
    win = gui.SudokuMaster()
    # win.show()
    win.onClickedConfirmButton()
    sys.exit(app.exec_())
