"""
FastAPI main application
"""

import os
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import (
    SolveRequest,
    SolveResponse,
    Step,
    GenerateRequest,
    GenerateResponse,
    ValidateRequest,
    ValidateResponse,
    HistoryResponse,
)
from utils.csv_handler import CSVHandler
from utils.validator import SudokuValidator
from ai.solvers import (
    backtracking,
    logic_solver,
    hybrid,
    dlx,
    optimized_backtracking,
    optimized_logic,
    ortools_solver,
)

# Initialize FastAPI app
app = FastAPI(
    title="Sudoku AI Solver",
    description="Web application with multiple AI algorithms to solve Sudoku puzzles",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Initialize utilities
csv_handler = CSVHandler()
validator = SudokuValidator()

# Solver mapping
SOLVERS = {
    # Original solvers
    "backtracking": backtracking.solve,
    "logic": logic_solver.solve,
    "hybrid": hybrid.solve,
    "dlx": dlx.solve,
    # Optimized solvers (new)
    "optimized_backtracking": optimized_backtracking.solve,
    "optimized_logic": optimized_logic.solve,
    "ortools": ortools_solver.solve,
}


@app.get("/")
async def home(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/solve", response_model=SolveResponse)
def solve_puzzle(request: SolveRequest) -> SolveResponse:
    """
    Solve a Sudoku puzzle using the specified algorithm

    Args:
        request: SolveRequest with board and algorithm choice

    Returns:
        SolveResponse with solved board and steps
    """
    try:
        # Validate input board
        is_valid, errors = validator.validate_board_detailed(request.board)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid board configuration",
                    "errors": errors,
                },
            )

        # Get solver function
        solver_func = SOLVERS.get(request.algorithm)
        if not solver_func:
            raise HTTPException(
                status_code=400, detail=f"Unknown algorithm: {request.algorithm}"
            )

        # Measure solving time
        start_time = time.perf_counter()
        solved_board, steps = solver_func(request.board)
        time_elapsed = time.perf_counter() - start_time

        # Convert steps to Pydantic models
        step_models = [Step(**step) for step in steps]

        # Save to history
        csv_handler.save_history(
            algorithm=request.algorithm,
            time_elapsed=time_elapsed,
            success=solved_board is not None,
            original_board=request.board,
            solved_board=solved_board,
        )

        return SolveResponse(
            success=solved_board is not None,
            solved_board=solved_board,
            steps=step_models,
            algorithm=request.algorithm,
            time_elapsed=time_elapsed,
            message=(
                "Puzzle solved successfully" if solved_board else "No solution found"
            ),
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/generate", response_model=GenerateResponse)
def generate_puzzle(request: GenerateRequest) -> GenerateResponse:
    """
    Generate a new Sudoku puzzle

    Args:
        request: GenerateRequest with difficulty level

    Returns:
        GenerateResponse with generated board
    """
    try:
        board, puzzle_id = csv_handler.get_puzzle(request.difficulty)

        return GenerateResponse(
            board=board, difficulty=request.difficulty, puzzle_id=puzzle_id
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/validate", response_model=ValidateResponse)
def validate_board(request: ValidateRequest) -> ValidateResponse:
    """
    Validate a Sudoku board configuration

    Args:
        request: ValidateRequest with board to validate

    Returns:
        ValidateResponse with validation result
    """
    try:
        is_valid, errors = validator.validate_board_detailed(request.board)

        return ValidateResponse(
            is_valid=is_valid,
            errors=errors,
            message="Board is valid" if is_valid else "Board has errors",
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/history", response_model=HistoryResponse)
def get_history(limit: int = Query(default=50, ge=1, le=500)) -> HistoryResponse:
    """
    Get solving history

    Args:
        limit: Maximum number of entries to return

    Returns:
        HistoryResponse with history entries
    """
    try:
        history = csv_handler.get_history(limit=limit)

        return HistoryResponse(history=history, total_count=len(history))

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/stats")
def get_statistics() -> Dict[str, Any]:
    """
    Get solver statistics

    Returns:
        Dictionary with statistics
    """
    try:
        stats = csv_handler.get_statistics()
        return stats

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
