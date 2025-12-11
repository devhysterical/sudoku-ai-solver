"""
Logic-based Sudoku solver
Uses constraint propagation and naked singles/hidden singles techniques
"""

from typing import List, Tuple, Dict, Set
import copy


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku using logic-based techniques

    Args:
        board: 9x9 Sudoku board with 0 for empty cells

    Returns:
        Tuple of (solved_board, steps)
    """
    board_copy = copy.deepcopy(board)
    steps = []

    # Initialize possible values for each cell
    possibilities = [
        [set(range(1, 10)) if board_copy[i][j] == 0 else set() for j in range(9)]
        for i in range(9)
    ]

    def get_possibilities(row: int, col: int) -> Set[int]:
        """Get possible values for a cell"""
        if board_copy[row][col] != 0:
            return set()

        possible = set(range(1, 10))

        # Remove values in same row
        for j in range(9):
            if board_copy[row][j] != 0:
                possible.discard(board_copy[row][j])

        # Remove values in same column
        for i in range(9):
            if board_copy[i][col] != 0:
                possible.discard(board_copy[i][col])

        # Remove values in same 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board_copy[i][j] != 0:
                    possible.discard(board_copy[i][j])

        return possible

    def update_possibilities():
        """Update all possibilities based on current board state"""
        for i in range(9):
            for j in range(9):
                if board_copy[i][j] == 0:
                    possibilities[i][j] = get_possibilities(i, j)

    def naked_singles() -> bool:
        """Find and fill cells with only one possibility"""
        changed = False
        for i in range(9):
            for j in range(9):
                if board_copy[i][j] == 0 and len(possibilities[i][j]) == 1:
                    value = list(possibilities[i][j])[0]
                    board_copy[i][j] = value
                    steps.append({"row": i, "col": j, "value": value, "action": "fill"})
                    changed = True
        return changed

    def hidden_singles() -> bool:
        """Find values that can only go in one place in a row/col/box"""
        changed = False

        # Check rows
        for i in range(9):
            for num in range(1, 10):
                possible_cols = [
                    j
                    for j in range(9)
                    if board_copy[i][j] == 0 and num in possibilities[i][j]
                ]
                if len(possible_cols) == 1:
                    j = possible_cols[0]
                    board_copy[i][j] = num
                    steps.append({"row": i, "col": j, "value": num, "action": "fill"})
                    changed = True

        # Check columns
        for j in range(9):
            for num in range(1, 10):
                possible_rows = [
                    i
                    for i in range(9)
                    if board_copy[i][j] == 0 and num in possibilities[i][j]
                ]
                if len(possible_rows) == 1:
                    i = possible_rows[0]
                    board_copy[i][j] = num
                    steps.append({"row": i, "col": j, "value": num, "action": "fill"})
                    changed = True

        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                for num in range(1, 10):
                    possible_cells = []
                    for i in range(box_row * 3, box_row * 3 + 3):
                        for j in range(box_col * 3, box_col * 3 + 3):
                            if board_copy[i][j] == 0 and num in possibilities[i][j]:
                                possible_cells.append((i, j))

                    if len(possible_cells) == 1:
                        i, j = possible_cells[0]
                        board_copy[i][j] = num
                        steps.append(
                            {"row": i, "col": j, "value": num, "action": "fill"}
                        )
                        changed = True

        return changed

    def is_complete() -> bool:
        """Check if puzzle is solved"""
        for i in range(9):
            for j in range(9):
                if board_copy[i][j] == 0:
                    return False
        return True

    # Main solving loop
    max_iterations = 100
    for iteration in range(max_iterations):
        update_possibilities()

        if is_complete():
            return board_copy, steps

        # Try naked singles
        if naked_singles():
            continue

        # Try hidden singles
        if hidden_singles():
            continue

        # If no progress made, logic solver cannot solve this puzzle
        break

    # If not complete, return None (logic solver failed)
    if is_complete():
        return board_copy, steps
    else:
        # Fall back to backtracking for remaining cells
        from . import backtracking

        remaining_steps = []
        result, remaining_steps = backtracking.solve(board_copy)
        if result:
            steps.extend(remaining_steps)
            return result, steps
        return None, steps
