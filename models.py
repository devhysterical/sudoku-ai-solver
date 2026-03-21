"""
Pydantic models for request and response validation
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


def validate_board_grid(board: List[List[int]]) -> List[List[int]]:
    """Validate a 9x9 Sudoku grid with values in the range 0-9."""
    if len(board) != 9:
        raise ValueError("Board must have exactly 9 rows")

    for row in board:
        if len(row) != 9:
            raise ValueError("Each row must have exactly 9 columns")
        for cell in row:
            if not isinstance(cell, int) or not (0 <= cell <= 9):
                raise ValueError("Cell values must be integers between 0 and 9")

    return board


class SudokuBoard(BaseModel):
    """Sudoku board representation (9x9 grid)"""

    board: List[List[int]] = Field(..., description="9x9 grid with 0 for empty cells")

    @field_validator("board")
    @classmethod
    def validate_board(cls, value: List[List[int]]) -> List[List[int]]:
        return validate_board_grid(value)


class SolveRequest(BaseModel):
    """Request to solve a Sudoku puzzle"""

    board: List[List[int]]
    algorithm: Literal[
        "backtracking",
        "logic",
        "hybrid",
        "dlx",
        "optimized_backtracking",
        "optimized_logic",
        "ortools",
    ] = Field(default="ortools", description="Solver algorithm to use")

    @field_validator("board")
    @classmethod
    def validate_board(cls, value: List[List[int]]) -> List[List[int]]:
        return validate_board_grid(value)


class Step(BaseModel):
    """Single step in the solving process"""

    row: int = Field(..., ge=0, lt=9)
    col: int = Field(..., ge=0, lt=9)
    value: int = Field(..., ge=0, le=9)
    action: Literal["fill", "highlight", "clear"]


class SolveResponse(BaseModel):
    """Response from solve endpoint"""

    success: bool
    solved_board: Optional[List[List[int]]] = None
    steps: List[Step] = Field(default_factory=list)
    algorithm: str
    time_elapsed: float
    message: Optional[str] = None


class GenerateRequest(BaseModel):
    """Request to generate a new puzzle"""

    difficulty: Literal["easy", "medium", "hard", "expert"] = Field(
        default="medium", description="Difficulty level of the puzzle"
    )


class GenerateResponse(BaseModel):
    """Response from generate endpoint"""

    board: List[List[int]]
    difficulty: str
    puzzle_id: Optional[str] = None


class ValidateRequest(BaseModel):
    """Request to validate a board state"""

    board: List[List[int]]

    @field_validator("board")
    @classmethod
    def validate_board(cls, value: List[List[int]]) -> List[List[int]]:
        return validate_board_grid(value)


class ValidateResponse(BaseModel):
    """Response from validate endpoint"""

    is_valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    message: str


class HistoryEntry(BaseModel):
    """Single history entry"""

    puzzle_id: str
    algorithm: str
    difficulty: str
    time_elapsed: float
    success: bool
    timestamp: str


class HistoryResponse(BaseModel):
    """Response from history endpoint"""

    history: List[HistoryEntry]
    total_count: int
