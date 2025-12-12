"""
Google OR-Tools Constraint Programming Solver
Professional-grade CSP solver - fastest solution
"""

from typing import List, Tuple, Dict
from ortools.sat.python import cp_model


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku using Google OR-Tools CP-SAT Solver

    This is a state-of-the-art constraint satisfaction solver
    that can solve even the hardest Sudoku puzzles in milliseconds.

    Args:
        board: 9x9 Sudoku board with 0 for empty cells

    Returns:
        Tuple of (solved_board, steps)
    """
    model = cp_model.CpModel()
    steps = []

    # Create decision variables (1-9 for each cell)
    cells = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                # Create variable for empty cells
                cells[(i, j)] = model.NewIntVar(1, 9, f"cell_{i}_{j}")
            else:
                # Fix value for pre-filled cells
                cells[(i, j)] = model.NewConstant(board[i][j])

    # Add row constraints: all values in a row must be different
    for i in range(9):
        model.AddAllDifferent([cells[(i, j)] for j in range(9)])

    # Add column constraints: all values in a column must be different
    for j in range(9):
        model.AddAllDifferent([cells[(i, j)] for i in range(9)])

    # Add box constraints: all values in a 3x3 box must be different
    for box_i in range(3):
        for box_j in range(3):
            box_cells = []
            for i in range(box_i * 3, box_i * 3 + 3):
                for j in range(box_j * 3, box_j * 3 + 3):
                    box_cells.append(cells[(i, j)])
            model.AddAllDifferent(box_cells)

    # Solve the model
    solver = cp_model.CpSolver()

    # Set solver parameters for optimization
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.num_search_workers = 1  # Single thread for consistency

    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract solution
        solved_board = [[0 for _ in range(9)] for _ in range(9)]

        for i in range(9):
            for j in range(9):
                value = solver.Value(cells[(i, j)])
                solved_board[i][j] = value

                # Generate steps for visualization
                if board[i][j] == 0:
                    steps.append(
                        {
                            "row": int(i),
                            "col": int(j),
                            "value": int(value),
                            "action": "fill",
                        }
                    )

        return solved_board, steps
    else:
        return None, steps


def solve_with_statistics(
    board: List[List[int]],
) -> Tuple[List[List[int]], List[Dict], Dict]:
    """
    Solve with additional statistics about the solving process

    Returns:
        Tuple of (solved_board, steps, statistics)
    """
    model = cp_model.CpModel()
    steps = []

    # Create decision variables
    cells = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                cells[(i, j)] = model.NewIntVar(1, 9, f"cell_{i}_{j}")
            else:
                cells[(i, j)] = model.NewConstant(board[i][j])

    # Add constraints (same as above)
    for i in range(9):
        model.AddAllDifferent([cells[(i, j)] for j in range(9)])

    for j in range(9):
        model.AddAllDifferent([cells[(i, j)] for i in range(9)])

    for box_i in range(3):
        for box_j in range(3):
            box_cells = []
            for i in range(box_i * 3, box_i * 3 + 3):
                for j in range(box_j * 3, box_j * 3 + 3):
                    box_cells.append(cells[(i, j)])
            model.AddAllDifferent(box_cells)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0

    status = solver.Solve(model)

    statistics = {
        "status": solver.StatusName(status),
        "wall_time": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "optimal": status == cp_model.OPTIMAL,
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        solved_board = [[0 for _ in range(9)] for _ in range(9)]

        for i in range(9):
            for j in range(9):
                value = solver.Value(cells[(i, j)])
                solved_board[i][j] = value

                if board[i][j] == 0:
                    steps.append(
                        {
                            "row": int(i),
                            "col": int(j),
                            "value": int(value),
                            "action": "fill",
                        }
                    )

        return solved_board, steps, statistics
    else:
        return None, steps, statistics
