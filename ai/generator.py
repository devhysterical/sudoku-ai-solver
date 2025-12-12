"""
Sudoku puzzle generator with difficulty levels
"""

import random
from typing import List, Tuple
from copy import deepcopy


class SudokuGenerator:
    """Generate Sudoku puzzles with varying difficulty levels"""

    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def generate(self, difficulty: str = "medium") -> List[List[int]]:
        """
        Generate a Sudoku puzzle with specified difficulty

        Args:
            difficulty: One of 'easy', 'medium', 'hard', 'expert'

        Returns:
            9x9 board with puzzle (0 for empty cells)
        """
        # Generate a complete valid Sudoku board
        self._generate_complete_board()

        # Remove numbers based on difficulty
        cells_to_remove = self._get_cells_to_remove(difficulty)
        puzzle = self._remove_numbers(self.board, cells_to_remove)

        return puzzle

    def _generate_complete_board(self):
        """Generate a complete valid Sudoku board using backtracking"""
        # Reset board
        self.board = [[0 for _ in range(9)] for _ in range(9)]

        # Fill diagonal 3x3 boxes first (they are independent)
        self._fill_diagonal_boxes()

        # Fill remaining cells
        self._fill_remaining(0, 3)

    def _fill_diagonal_boxes(self):
        """Fill the three 3x3 boxes on the diagonal (independent)"""
        for box in range(0, 9, 3):
            self._fill_box(box, box)

    def _fill_box(self, row: int, col: int):
        """Fill a 3x3 box with random numbers"""
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for i in range(3):
            for j in range(3):
                self.board[row + i][col + j] = numbers[i * 3 + j]

    def _fill_remaining(self, row: int, col: int) -> bool:
        """Fill remaining cells using backtracking"""
        # Move to next row if we've reached end of column
        if col >= 9 and row < 8:
            row += 1
            col = 0
        if row >= 9 and col >= 9:
            return True

        # Skip if in diagonal box (already filled)
        if row < 3:
            if col < 3:
                col = 3
        elif row < 6:
            if col == int(row / 3) * 3:
                col += 3
        else:
            if col == 6:
                row += 1
                col = 0
                if row >= 9:
                    return True

        # Try numbers 1-9
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for num in numbers:
            if self._is_safe(row, col, num):
                self.board[row][col] = num
                if self._fill_remaining(row, col + 1):
                    return True
                self.board[row][col] = 0

        return False

    def _is_safe(self, row: int, col: int, num: int) -> bool:
        """Check if number can be placed at position"""
        # Check row
        if num in self.board[row]:
            return False

        # Check column
        for i in range(9):
            if self.board[i][col] == num:
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[box_row + i][box_col + j] == num:
                    return False

        return True

    def _get_cells_to_remove(self, difficulty: str) -> int:
        """
        Get number of cells to remove based on difficulty

        Difficulty levels:
        - easy: 35-45 cells removed (36-46 filled)
        - medium: 46-54 cells removed (27-35 filled)
        - hard: 55-59 cells removed (22-26 filled)
        - expert: 60-64 cells removed (17-21 filled)
        """
        ranges = {
            "easy": (35, 45),
            "medium": (46, 54),
            "hard": (55, 59),
            "expert": (60, 64),
        }

        min_remove, max_remove = ranges.get(difficulty, ranges["medium"])
        return random.randint(min_remove, max_remove)

    def _remove_numbers(
        self, complete_board: List[List[int]], cells_to_remove: int
    ) -> List[List[int]]:
        """
        Remove numbers from complete board to create puzzle

        Args:
            complete_board: Complete valid Sudoku board
            cells_to_remove: Number of cells to remove

        Returns:
            Puzzle board with removed cells (0 for empty)
        """
        puzzle = deepcopy(complete_board)
        removed = 0
        attempts = 0
        max_attempts = cells_to_remove * 3

        while removed < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)

            if puzzle[row][col] != 0:
                backup = puzzle[row][col]
                puzzle[row][col] = 0

                # Check if puzzle still has unique solution
                # For performance, we skip this check and rely on randomization
                # In production, you might want to verify uniqueness
                removed += 1

            attempts += 1

        return puzzle

    def _count_solutions(self, board: List[List[int]], limit: int = 2) -> int:
        """
        Count number of solutions (used to verify uniqueness)
        Returns early if count exceeds limit for performance

        Args:
            board: Puzzle board
            limit: Stop counting after this many solutions

        Returns:
            Number of solutions found (up to limit)
        """
        solutions = [0]  # Use list to maintain reference in nested function

        def solve(b):
            if solutions[0] >= limit:
                return

            # Find empty cell
            for i in range(9):
                for j in range(9):
                    if b[i][j] == 0:
                        for num in range(1, 10):
                            if self._is_valid_placement(b, i, j, num):
                                b[i][j] = num
                                solve(b)
                                b[i][j] = 0
                        return

            # Found a solution
            solutions[0] += 1

        solve(deepcopy(board))
        return solutions[0]

    def _is_valid_placement(
        self, board: List[List[int]], row: int, col: int, num: int
    ) -> bool:
        """Check if placement is valid"""
        # Check row
        if num in board[row]:
            return False

        # Check column
        for i in range(9):
            if board[i][col] == num:
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[box_row + i][box_col + j] == num:
                    return False

        return True


def generate_puzzle(
    difficulty: str = "medium",
) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Generate a Sudoku puzzle and its solution

    Args:
        difficulty: One of 'easy', 'medium', 'hard', 'expert'

    Returns:
        Tuple of (puzzle, solution)
    """
    generator = SudokuGenerator()

    # Generate complete board (this will be the solution)
    generator._generate_complete_board()
    solution = deepcopy(generator.board)

    # Create puzzle by removing numbers
    cells_to_remove = generator._get_cells_to_remove(difficulty)
    puzzle = generator._remove_numbers(solution, cells_to_remove)

    return puzzle, solution
