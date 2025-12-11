"""
Backtracking algorithm for Sudoku solving
Uses depth-first search with backtracking to find solution
"""

from typing import List, Tuple, Dict
import copy


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku puzzle using backtracking algorithm

    Args:
        board: 9x9 Sudoku board with 0 for empty cells

    Returns:
        Tuple of (solved_board, steps) where steps is list of solving steps
    """
    # Create a copy to avoid modifying original
    board_copy = copy.deepcopy(board)
    steps = []

    def is_valid(row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid"""
        # Check row
        if num in board_copy[row]:
            return False

        # Check column
        for i in range(9):
            if board_copy[i][col] == num:
                return False

        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board_copy[i][j] == num:
                    return False

        return True

    def find_empty() -> Tuple[int, int]:
        """Find next empty cell (with 0)"""
        for i in range(9):
            for j in range(9):
                if board_copy[i][j] == 0:
                    return i, j
        return -1, -1

    def backtrack() -> bool:
        """Recursive backtracking solver"""
        row, col = find_empty()

        # No empty cells left - puzzle solved
        if row == -1:
            return True

        # Try numbers 1-9
        for num in range(1, 10):
            if is_valid(row, col, num):
                # Place number
                board_copy[row][col] = num
                steps.append({"row": row, "col": col, "value": num, "action": "fill"})

                # Recursively try to solve
                if backtrack():
                    return True

                # Backtrack if no solution found
                board_copy[row][col] = 0
                steps.append({"row": row, "col": col, "value": 0, "action": "clear"})

        return False

    # Solve the puzzle
    success = backtrack()

    if success:
        return board_copy, steps
    else:
        return None, steps
