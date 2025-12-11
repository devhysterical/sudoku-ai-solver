"""
Utility functions for Sudoku board validation
"""
from typing import List, Tuple, Dict, Any


class SudokuValidator:
    """Validates Sudoku board configurations"""
    
    @staticmethod
    def is_valid_value(value: int) -> bool:
        """Check if value is valid (0-9)"""
        return 0 <= value <= 9
    
    @staticmethod
    def validate_board(board: List[List[int]]) -> bool:
        """
        Validate basic board structure and values
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            True if board structure is valid
        """
        if not board or len(board) != 9:
            return False
        
        for row in board:
            if not row or len(row) != 9:
                return False
            for cell in row:
                if not SudokuValidator.is_valid_value(cell):
                    return False
        
        return True
    
    @staticmethod
    def validate_board_detailed(board: List[List[int]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Detailed validation with error reporting
        
        Args:
            board: 9x9 Sudoku board
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check structure
        if not SudokuValidator.validate_board(board):
            errors.append({
                'type': 'structure',
                'message': 'Invalid board structure (must be 9x9)'
            })
            return False, errors
        
        # Check rows for duplicates
        for i, row in enumerate(board):
            seen = set()
            for j, val in enumerate(row):
                if val != 0 and val in seen:
                    errors.append({
                        'type': 'duplicate',
                        'location': 'row',
                        'row': i,
                        'col': j,
                        'value': val,
                        'message': f'Duplicate {val} in row {i+1}'
                    })
                if val != 0:
                    seen.add(val)
        
        # Check columns for duplicates
        for j in range(9):
            seen = set()
            for i in range(9):
                val = board[i][j]
                if val != 0 and val in seen:
                    errors.append({
                        'type': 'duplicate',
                        'location': 'column',
                        'row': i,
                        'col': j,
                        'value': val,
                        'message': f'Duplicate {val} in column {j+1}'
                    })
                if val != 0:
                    seen.add(val)
        
        # Check 3x3 boxes for duplicates
        for box_row in range(3):
            for box_col in range(3):
                seen = set()
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        val = board[row][col]
                        if val != 0 and val in seen:
                            errors.append({
                                'type': 'duplicate',
                                'location': 'box',
                                'row': row,
                                'col': col,
                                'value': val,
                                'message': f'Duplicate {val} in 3x3 box'
                            })
                        if val != 0:
                            seen.add(val)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_placement(board: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing num at (row, col) is valid
        
        Args:
            board: Current board state
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)
            
        Returns:
            True if placement is valid
        """
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False
        
        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        
        return True
