from PyQt5.QtCore import QThread, pyqtSignal
from random import shuffle
import logging
from algorithm.elimination_solver import Solver


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


