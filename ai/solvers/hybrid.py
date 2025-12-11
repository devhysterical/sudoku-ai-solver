"""
Hybrid Sudoku solver
Combines logic-based techniques with backtracking for optimal performance
"""
from typing import List, Tuple, Dict, Set
import copy


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku using hybrid approach (logic + backtracking)
    
    Args:
        board: 9x9 Sudoku board with 0 for empty cells
        
    Returns:
        Tuple of (solved_board, steps)
    """
    board_copy = copy.deepcopy(board)
    steps = []
    
    def get_possibilities(row: int, col: int) -> Set[int]:
        """Get possible values for a cell"""
        if board_copy[row][col] != 0:
            return set()
        
        possible = set(range(1, 10))
        
        # Remove values in row
        for j in range(9):
            if board_copy[row][j] != 0:
                possible.discard(board_copy[row][j])
        
        # Remove values in column
        for i in range(9):
            if board_copy[i][col] != 0:
                possible.discard(board_copy[i][col])
        
        # Remove values in box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board_copy[i][j] != 0:
                    possible.discard(board_copy[i][j])
        
        return possible
    
    def apply_logic() -> bool:
        """Apply logic techniques until no more progress"""
        changed = True
        overall_changed = False
        
        while changed:
            changed = False
            
            # Naked singles
            for i in range(9):
                for j in range(9):
                    if board_copy[i][j] == 0:
                        possible = get_possibilities(i, j)
                        if len(possible) == 1:
                            value = list(possible)[0]
                            board_copy[i][j] = value
                            steps.append({
                                'row': i,
                                'col': j,
                                'value': value,
                                'action': 'fill'
                            })
                            changed = True
                            overall_changed = True
                        elif len(possible) == 0:
                            # Invalid state
                            return overall_changed
        
        return overall_changed
    
    def find_best_cell() -> Tuple[int, int]:
        """Find empty cell with fewest possibilities (MRV heuristic)"""
        min_choices = 10
        best_cell = (-1, -1)
        
        for i in range(9):
            for j in range(9):
                if board_copy[i][j] == 0:
                    possible = get_possibilities(i, j)
                    if len(possible) < min_choices:
                        min_choices = len(possible)
                        best_cell = (i, j)
        
        return best_cell
    
    def backtrack() -> bool:
        """Smart backtracking with logic propagation"""
        # Apply logic first
        apply_logic()
        
        # Find best cell to fill
        row, col = find_best_cell()
        
        if row == -1:
            # No empty cells - solved
            return True
        
        # Get possible values
        possible = get_possibilities(row, col)
        
        if len(possible) == 0:
            # No valid values - backtrack
            return False
        
        # Try each possibility
        for num in possible:
            # Save state
            old_board = copy.deepcopy(board_copy)
            old_steps_len = len(steps)
            
            # Place number
            board_copy[row][col] = num
            steps.append({
                'row': row,
                'col': col,
                'value': num,
                'action': 'fill'
            })
            
            # Recursively solve
            if backtrack():
                return True
            
            # Restore state if failed
            for i in range(9):
                for j in range(9):
                    board_copy[i][j] = old_board[i][j]
            
            # Remove failed steps
            while len(steps) > old_steps_len:
                steps.pop()
            
            steps.append({
                'row': row,
                'col': col,
                'value': 0,
                'action': 'clear'
            })
        
        return False
    
    # Solve using hybrid approach
    success = backtrack()
    
    if success:
        return board_copy, steps
    else:
        return None, steps
