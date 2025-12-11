"""
Dancing Links X (DLX) algorithm for Sudoku
Implements Knuth's Algorithm X with Dancing Links for exact cover problem
"""
from typing import List, Tuple, Dict, Optional
import copy


class DancingNode:
    """Node in the dancing links structure"""
    def __init__(self, row_id: int = -1):
        self.left: Optional['DancingNode'] = self
        self.right: Optional['DancingNode'] = self
        self.up: Optional['DancingNode'] = self
        self.down: Optional['DancingNode'] = self
        self.column: Optional['ColumnNode'] = None
        self.row_id: int = row_id


class ColumnNode(DancingNode):
    """Column header node"""
    def __init__(self, name: str = ""):
        super().__init__()
        self.size: int = 0
        self.name: str = name
        self.column = self


def solve(board: List[List[int]]) -> Tuple[List[List[int]], List[Dict]]:
    """
    Solve Sudoku using Dancing Links X algorithm
    
    Args:
        board: 9x9 Sudoku board with 0 for empty cells
        
    Returns:
        Tuple of (solved_board, steps)
    """
    board_copy = copy.deepcopy(board)
    steps = []
    solution = []
    
    def create_exact_cover_matrix() -> Tuple[DancingNode, Dict]:
        """Create the exact cover matrix for Sudoku"""
        # 4 constraints: cell, row, column, box
        # Total columns: 9*9 (cells) + 9*9 (rows) + 9*9 (cols) + 9*9 (boxes) = 324
        
        header = ColumnNode("header")
        columns = {}
        
        # Create column nodes
        for i in range(324):
            col = ColumnNode(f"col_{i}")
            columns[i] = col
            col.left = header.left
            col.right = header
            header.left.right = col
            header.left = col
        
        # Create rows for each possible move
        row_id = 0
        row_mapping = {}
        
        for row in range(9):
            for col in range(9):
                for num in range(1, 10):
                    # Skip if cell already filled
                    if board_copy[row][col] != 0 and board_copy[row][col] != num:
                        continue
                    
                    # Calculate constraint column indices
                    cell_idx = row * 9 + col
                    row_idx = 81 + row * 9 + (num - 1)
                    col_idx = 162 + col * 9 + (num - 1)
                    box_idx = 243 + ((row // 3) * 3 + col // 3) * 9 + (num - 1)
                    
                    indices = [cell_idx, row_idx, col_idx, box_idx]
                    
                    # Create nodes for this row
                    row_nodes = []
                    for idx in indices:
                        node = DancingNode(row_id)
                        node.column = columns[idx]
                        
                        # Insert into column
                        node.up = columns[idx].up
                        node.down = columns[idx]
                        columns[idx].up.down = node
                        columns[idx].up = node
                        columns[idx].size += 1
                        
                        row_nodes.append(node)
                    
                    # Link row nodes horizontally
                    for i in range(len(row_nodes)):
                        row_nodes[i].left = row_nodes[i - 1]
                        row_nodes[i].right = row_nodes[(i + 1) % len(row_nodes)]
                    
                    row_mapping[row_id] = (row, col, num)
                    row_id += 1
        
        return header, row_mapping
    
    def cover(col: ColumnNode):
        """Cover a column"""
        col.right.left = col.left
        col.left.right = col.right
        
        i = col.down
        while i != col:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down
    
    def uncover(col: ColumnNode):
        """Uncover a column"""
        i = col.up
        while i != col:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        
        col.right.left = col
        col.left.right = col
    
    def search(k: int, header: DancingNode, row_mapping: Dict) -> bool:
        """Recursive search for solution"""
        if header.right == header:
            # All columns covered - solution found
            for row_id in solution:
                row, col, num = row_mapping[row_id]
                if board_copy[row][col] == 0:
                    board_copy[row][col] = num
                    steps.append({
                        'row': row,
                        'col': col,
                        'value': num,
                        'action': 'fill'
                    })
            return True
        
        # Choose column with minimum size (S heuristic)
        min_size = float('inf')
        col = None
        j = header.right
        while j != header:
            if j.size < min_size:
                min_size = j.size
                col = j
            j = j.right
        
        if col is None or col.size == 0:
            return False
        
        cover(col)
        
        r = col.down
        while r != col:
            solution.append(r.row_id)
            
            j = r.right
            while j != r:
                cover(j.column)
                j = j.right
            
            if search(k + 1, header, row_mapping):
                return True
            
            solution.pop()
            
            j = r.left
            while j != r:
                uncover(j.column)
                j = j.left
            
            r = r.down
        
        uncover(col)
        return False
    
    # Build and solve
    try:
        header, row_mapping = create_exact_cover_matrix()
        success = search(0, header, row_mapping)
        
        if success:
            return board_copy, steps
        else:
            return None, steps
    except Exception as e:
        # Fallback to backtracking if DLX fails
        from . import backtracking
        return backtracking.solve(board)
