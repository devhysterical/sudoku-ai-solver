"""
FastAPI main application
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any

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
from ai.solvers import backtracking, logic_solver, hybrid, dlx

# Initialize FastAPI app
app = FastAPI(
    title="Sudoku AI Solver",
    description="Web application with multiple AI algorithms to solve Sudoku puzzles",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize utilities
csv_handler = CSVHandler()
validator = SudokuValidator()

# Solver mapping
SOLVERS = {
    "backtracking": backtracking.solve,
    "logic": logic_solver.solve,
    "hybrid": hybrid.solve,
    "dlx": dlx.solve,
}


@app.get("/")
async def home(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/solve", response_model=SolveResponse)
async def solve_puzzle(request: SolveRequest) -> SolveResponse:
    """
    Solve a Sudoku puzzle using the specified algorithm

    Args:
        request: SolveRequest with board and algorithm choice

    Returns:
        SolveResponse with solved board and steps
    """
    try:
        # Validate input board
        if not validator.validate_board(request.board):
            raise HTTPException(status_code=400, detail="Invalid board configuration")

        # Get solver function
        solver_func = SOLVERS.get(request.algorithm)
        if not solver_func:
            raise HTTPException(
                status_code=400, detail=f"Unknown algorithm: {request.algorithm}"
            )

        # Measure solving time
        start_time = time.time()
        solved_board, steps = solver_func(request.board)
        time_elapsed = time.time() - start_time

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_puzzle(request: GenerateRequest) -> GenerateResponse:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate", response_model=ValidateResponse)
async def validate_board(request: ValidateRequest) -> ValidateResponse:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", response_model=HistoryResponse)
async def get_history(limit: int = 50) -> HistoryResponse:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics() -> Dict[str, Any]:
    """
    Get solver statistics

    Returns:
        Dictionary with statistics
    """
    try:
        stats = csv_handler.get_statistics()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
