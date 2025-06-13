from sudoku import Sudoku
from src.utils.logger import default_logger


class SudokuSolverError(Exception):
    """Custom exception for Sudoku solver errors."""
    pass


class SudokuSolver:
    """Class for handling Sudoku puzzle creation and solving."""
    
    def __init__(self):
        """Initialize the Sudoku solver."""
        self.puzzle = None
        self.solution = None

    def create_puzzle(self, digits):
        """Create a Sudoku puzzle from a 2D array of digits."""
        try:
            self.puzzle = Sudoku(3, 3, digits)
            default_logger.info("Successfully created Sudoku puzzle")
            return self.puzzle
        except Exception as e:
            default_logger.error(f"Error creating Sudoku puzzle: {str(e)}")
            raise SudokuSolverError(f"Failed to create Sudoku puzzle: {str(e)}")

    def solve(self):
        """Solve the current Sudoku puzzle."""
        try:
            if self.puzzle is None:
                raise SudokuSolverError("No puzzle has been created yet")
            
            self.solution = self.puzzle.solve()
            default_logger.info("Successfully solved Sudoku puzzle")
            return self.solution
        except Exception as e:
            default_logger.error(f"Error solving Sudoku puzzle: {str(e)}")
            raise SudokuSolverError(f"Failed to solve Sudoku puzzle: {str(e)}")

    def get_puzzle(self):
        """Get the current puzzle."""
        return self.puzzle

    def get_solution(self):
        """Get the current solution."""
        return self.solution


sudoku_solver = SudokuSolver()
