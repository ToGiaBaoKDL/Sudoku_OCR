import unittest
import numpy as np
from src.core.sudoku_solver import SudokuSolver


class TestSudokuSolver(unittest.TestCase):
    def setUp(self):
        self.sudoku_solver = SudokuSolver()
        # Valid Sudoku grid
        self.valid_grid = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        # Invalid Sudoku grid (duplicate numbers in row)
        self.invalid_grid = [
            [5, 5, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        # Empty grid
        self.empty_grid = [[0 for _ in range(9)] for _ in range(9)]
        # Solved grid
        self.solved_grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]

    def test_create_sudoku_puzzle(self):
        # Test with valid grid
        puzzle = self.sudoku_solver.create_puzzle(self.valid_grid)
        self.assertIsNotNone(puzzle)
        self.assertEqual(puzzle.board.shape, (9, 9))
        
        # Test with empty grid
        puzzle = self.sudoku_solver.create_puzzle(self.empty_grid)
        self.assertIsNotNone(puzzle)
        self.assertEqual(puzzle.board.shape, (9, 9))
        self.assertTrue(np.all(puzzle.board == 0))

    def test_solve_sudoku(self):
        # Test solving valid puzzle
        puzzle = self.sudoku_solver.create_puzzle(self.valid_grid)
        solution = self.sudoku_solver.solve(puzzle)
        self.assertIsNotNone(solution)
        self.assertTrue(solution.is_valid())
        
        # Test solving empty puzzle
        puzzle = self.sudoku_solver.create_puzzle(self.empty_grid)
        solution = self.sudoku_solver.solve(puzzle)
        self.assertIsNotNone(solution)
        self.assertTrue(solution.is_valid())

    def test_invalid_puzzle(self):
        # Test with invalid grid
        with self.assertRaises(ValueError):
            self.sudoku_solver.create_puzzle(self.invalid_grid)

    def test_solved_puzzle(self):
        # Test with already solved grid
        puzzle = self.sudoku_solver.create_puzzle(self.solved_grid)
        solution = self.sudoku_solver.solve(puzzle)
        self.assertIsNotNone(solution)
        self.assertTrue(solution.is_valid())
        self.assertTrue(np.array_equal(solution.board, np.array(self.solved_grid)))

    def test_puzzle_validation(self):
        # Test puzzle validation
        puzzle = self.sudoku_solver.create_puzzle(self.valid_grid)
        self.assertTrue(puzzle.is_valid())
        
        # Test invalid puzzle
        puzzle = self.sudoku_solver.create_puzzle(self.invalid_grid)
        self.assertFalse(puzzle.is_valid())


if __name__ == '__main__':
    unittest.main()
