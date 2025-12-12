"""
Optimized Logic-based Solver using NumPy
Implements advanced constraint propagation techniques
"""

from typing import List, Tuple, Dict, Set
import numpy as np


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku using optimized logic techniques with NumPy

    Args:
        board: 9x9 Sudoku board with 0 for empty cells

    Returns:
        Tuple of (solved_board, steps)
    """
    # Convert to NumPy for faster operations
    board_array = np.array(board, dtype=np.int8)
    steps = []

    # Use sets for O(1) lookups
    row_sets = [set() for _ in range(9)]
    col_sets = [set() for _ in range(9)]
    box_sets = [set() for _ in range(9)]

    # Pre-compute box mapping
    box_map = np.array([[(i // 3) * 3 + (j // 3) for j in range(9)] for i in range(9)])

    # Initialize constraints
    for i in range(9):
        for j in range(9):
            if board_array[i, j] != 0:
                num = board_array[i, j]
                row_sets[i].add(num)
                col_sets[j].add(num)
                box_sets[box_map[i, j]].add(num)

    def get_candidates(row: int, col: int) -> Set[int]:
        """Get valid candidates for a cell"""
        if board_array[row, col] != 0:
            return set()

        box_idx = box_map[row, col]
        all_nums = set(range(1, 10))
        return all_nums - row_sets[row] - col_sets[col] - box_sets[box_idx]

    def place_number(row: int, col: int, num: int):
        """Place a number and update constraints"""
        board_array[row, col] = num
        row_sets[row].add(num)
        col_sets[col].add(num)
        box_sets[box_map[row, col]].add(num)
        steps.append(
            {"row": int(row), "col": int(col), "value": int(num), "action": "fill"}
        )

    def naked_singles() -> bool:
        """Find cells with only one candidate"""
        changed = False
        for i in range(9):
            for j in range(9):
                if board_array[i, j] == 0:
                    candidates = get_candidates(i, j)
                    if len(candidates) == 1:
                        place_number(i, j, list(candidates)[0])
                        changed = True
                    elif len(candidates) == 0:
                        return changed  # Invalid state
        return changed

    def hidden_singles_row() -> bool:
        """Find numbers that can only go in one place in a row"""
        changed = False
        for i in range(9):
            for num in range(1, 10):
                if num in row_sets[i]:
                    continue

                possible_cols = []
                for j in range(9):
                    if board_array[i, j] == 0 and num in get_candidates(i, j):
                        possible_cols.append(j)

                if len(possible_cols) == 1:
                    place_number(i, possible_cols[0], num)
                    changed = True
        return changed

    def hidden_singles_col() -> bool:
        """Find numbers that can only go in one place in a column"""
        changed = False
        for j in range(9):
            for num in range(1, 10):
                if num in col_sets[j]:
                    continue

                possible_rows = []
                for i in range(9):
                    if board_array[i, j] == 0 and num in get_candidates(i, j):
                        possible_rows.append(i)

                if len(possible_rows) == 1:
                    place_number(possible_rows[0], j, num)
                    changed = True
        return changed

    def hidden_singles_box() -> bool:
        """Find numbers that can only go in one place in a box"""
        changed = False
        for box_idx in range(9):
            box_i, box_j = (box_idx // 3) * 3, (box_idx % 3) * 3

            for num in range(1, 10):
                if num in box_sets[box_idx]:
                    continue

                possible_cells = []
                for i in range(box_i, box_i + 3):
                    for j in range(box_j, box_j + 3):
                        if board_array[i, j] == 0 and num in get_candidates(i, j):
                            possible_cells.append((i, j))

                if len(possible_cells) == 1:
                    row, col = possible_cells[0]
                    place_number(row, col, num)
                    changed = True
        return changed

    def apply_logic() -> bool:
        """Apply all logic techniques until no progress"""
        progress = True
        while progress:
            progress = False
            progress = naked_singles() or progress
            progress = hidden_singles_row() or progress
            progress = hidden_singles_col() or progress
            progress = hidden_singles_box() or progress
        return True

    def is_solved() -> bool:
        """Check if puzzle is completely solved"""
        return not np.any(board_array == 0)

    def backtrack() -> bool:
        """Fallback to backtracking if logic alone isn't enough"""
        if is_solved():
            return True

        # Find cell with minimum candidates (MRV)
        min_candidates = 10
        best_cell = None

        for i in range(9):
            for j in range(9):
                if board_array[i, j] == 0:
                    candidates = get_candidates(i, j)
                    if len(candidates) == 0:
                        return False
                    if len(candidates) < min_candidates:
                        min_candidates = len(candidates)
                        best_cell = (i, j, candidates)

        if best_cell is None:
            return True

        row, col, candidates = best_cell

        for num in candidates:
            # Save state
            old_board = board_array.copy()
            old_row_sets = [s.copy() for s in row_sets]
            old_col_sets = [s.copy() for s in col_sets]
            old_box_sets = [s.copy() for s in box_sets]

            # Try this number
            place_number(row, col, num)
            apply_logic()

            if backtrack():
                return True

            # Restore state
            board_array[:] = old_board
            row_sets[:] = old_row_sets
            col_sets[:] = old_col_sets
            box_sets[:] = old_box_sets
            steps.append(
                {"row": int(row), "col": int(col), "value": 0, "action": "clear"}
            )

        return False

    # Main solving logic
    apply_logic()

    if not is_solved():
        success = backtrack()
        if not success:
            return None, steps

    return board_array.tolist(), steps
