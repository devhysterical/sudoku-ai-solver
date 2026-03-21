"""
CSV file handler for puzzles and history
"""

import ast
import csv
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple
import os
import uuid

import pandas as pd

from ai.generator import generate_puzzle


class CSVHandler:
    """Handle CSV operations for puzzles and history"""

    PUZZLE_COLUMNS = ["id", "difficulty", "board", "solution"]
    HISTORY_COLUMNS = [
        "timestamp",
        "puzzle_id",
        "algorithm",
        "difficulty",
        "time_elapsed",
        "success",
    ]

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = self.base_dir / "data"
        self.puzzles_file = self.data_dir / "puzzles.csv"
        self.history_file = self.data_dir / "solver_history.csv"
        self.max_stored_puzzles = int(os.getenv("MAX_STORED_PUZZLES", "500"))
        self.max_history_rows = int(os.getenv("MAX_HISTORY_ROWS", "2000"))
        self._lock = Lock()
        self._initialize_files()

    def _initialize_files(self):
        """Initialize CSV files if they don't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize puzzles.csv
        if not self.puzzles_file.exists():
            df = pd.DataFrame(columns=self.PUZZLE_COLUMNS)
            df.to_csv(self.puzzles_file, index=False)
            self._generate_sample_puzzles()

        # Initialize solver_history.csv
        if not self.history_file.exists():
            df = pd.DataFrame(columns=self.HISTORY_COLUMNS)
            df.to_csv(self.history_file, index=False)

    def _generate_sample_puzzles(self):
        """Generate sample puzzles for testing"""
        # Easy puzzle
        easy_puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

        # Medium puzzle
        medium_puzzle = [
            [0, 0, 0, 6, 0, 0, 4, 0, 0],
            [7, 0, 0, 0, 0, 3, 6, 0, 0],
            [0, 0, 0, 0, 9, 1, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 1, 8, 0, 0, 0, 3],
            [0, 0, 0, 3, 0, 6, 0, 4, 5],
            [0, 4, 0, 2, 0, 0, 0, 6, 0],
            [9, 0, 3, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 1, 0, 0],
        ]

        # Hard puzzle
        hard_puzzle = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 8, 5],
            [0, 0, 1, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 5, 0, 7, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 1, 0, 0],
            [0, 9, 0, 0, 0, 0, 0, 0, 0],
            [5, 0, 0, 0, 0, 0, 0, 7, 3],
            [0, 0, 2, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 9],
        ]

        puzzles = [
            {
                "id": str(uuid.uuid4()),
                "difficulty": "easy",
                "board": str(easy_puzzle),
                "solution": None,
            },
            {
                "id": str(uuid.uuid4()),
                "difficulty": "medium",
                "board": str(medium_puzzle),
                "solution": None,
            },
            {
                "id": str(uuid.uuid4()),
                "difficulty": "hard",
                "board": str(hard_puzzle),
                "solution": None,
            },
        ]

        df = pd.DataFrame(puzzles, columns=self.PUZZLE_COLUMNS)
        df.to_csv(self.puzzles_file, index=False)

    def _read_csv_compat(self, file_path: Path, columns: List[str]) -> pd.DataFrame:
        """Read a CSV file while tolerating older schema variants."""
        if not file_path.exists():
            return pd.DataFrame(columns=columns)

        try:
            frame = pd.read_csv(file_path)
        except pd.errors.ParserError:
            if file_path != self.puzzles_file:
                raise
            rows = []
            with file_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    rows.append(
                        {
                            "id": row[0] if len(row) > 0 else "",
                            "difficulty": row[1] if len(row) > 1 else "medium",
                            "board": row[2] if len(row) > 2 else "[]",
                            "solution": row[3] if len(row) > 3 else None,
                        }
                    )
            frame = pd.DataFrame(rows, columns=self.PUZZLE_COLUMNS)

        for column in columns:
            if column not in frame.columns:
                frame[column] = None

        return frame[columns]

    def _append_dataframe(
        self, file_path: Path, frame: pd.DataFrame, max_rows: Optional[int] = None
    ) -> None:
        """Append rows to a CSV file and optionally keep only the newest rows."""
        columns = self.PUZZLE_COLUMNS if file_path == self.puzzles_file else self.HISTORY_COLUMNS
        with self._lock:
            existing = self._read_csv_compat(file_path, columns)
            if not existing.empty:
                frame = pd.concat([existing, frame], ignore_index=True)
            frame = frame[columns]
            if max_rows is not None and len(frame) > max_rows:
                frame = frame.tail(max_rows).reset_index(drop=True)
            frame.to_csv(file_path, index=False)

    def get_puzzle(
        self, difficulty: str = "medium", use_generator: bool = True
    ) -> Tuple[List[List[int]], str]:
        """
        Get a puzzle of specified difficulty

        Args:
            difficulty: Difficulty level (easy/medium/hard/expert)
            use_generator: If True, generate new puzzle; if False, use stored puzzles

        Returns:
            Tuple of (board, puzzle_id)
        """
        puzzle_id = str(uuid.uuid4())

        if use_generator:
            # Generate new puzzle using the generator
            board, solution = generate_puzzle(difficulty)

            # Optionally save to CSV for future reference
            self._save_puzzle_to_csv(puzzle_id, difficulty, board, solution)

            return board, puzzle_id
        else:
            # Use stored puzzles (legacy behavior)
            df = self._read_csv_compat(self.puzzles_file, self.PUZZLE_COLUMNS)

            # Filter by difficulty
            puzzles = df[df["difficulty"] == difficulty]

            if len(puzzles) == 0:
                # Fallback to any puzzle
                puzzles = df

            # Select random puzzle
            puzzle = puzzles.sample(n=1).iloc[0]

            # Parse board string to list
            board = ast.literal_eval(puzzle["board"])

            return board, puzzle["id"]

    def _save_puzzle_to_csv(
        self,
        puzzle_id: str,
        difficulty: str,
        board: List[List[int]],
        solution: List[List[int]],
    ):
        """
        Save generated puzzle to CSV file

        Args:
            puzzle_id: Unique puzzle identifier
            difficulty: Difficulty level
            board: Puzzle board
            solution: Solution board
        """
        entry = {
            "id": puzzle_id,
            "difficulty": difficulty,
            "board": str(board),
            "solution": str(solution),
        }

        self._append_dataframe(
            self.puzzles_file,
            pd.DataFrame([entry]),
            max_rows=self.max_stored_puzzles,
        )

    def save_history(
        self,
        algorithm: str,
        time_elapsed: float,
        success: bool,
        original_board: List[List[int]],
        solved_board: Optional[List[List[int]]] = None,
    ):
        """
        Save solving attempt to history

        Args:
            algorithm: Algorithm used
            time_elapsed: Time taken to solve
            success: Whether solution was found
            original_board: Original puzzle board
            solved_board: Solved board (if successful)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "puzzle_id": str(uuid.uuid4()),
            "algorithm": algorithm,
            "difficulty": "unknown",
            "time_elapsed": round(time_elapsed, 4),
            "success": success,
        }

        self._append_dataframe(
            self.history_file,
            pd.DataFrame([entry]),
            max_rows=self.max_history_rows,
        )

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get solving history

        Args:
            limit: Maximum number of entries

        Returns:
            List of history entries
        """
        if not self.history_file.exists():
            return []

        with self._lock:
            df = self._read_csv_compat(self.history_file, self.HISTORY_COLUMNS)

        # Sort by timestamp descending
        df = df.sort_values("timestamp", ascending=False)

        # Limit results
        df = df.head(limit)

        return df.to_dict("records")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from history

        Returns:
            Dictionary with statistics
        """
        if not self.history_file.exists():
            return {
                "total_solves": 0,
                "success_rate": 0,
                "avg_time": 0,
                "by_algorithm": {},
            }

        with self._lock:
            df = self._read_csv_compat(self.history_file, self.HISTORY_COLUMNS)

        stats = {
            "total_solves": len(df),
            "success_rate": (df["success"].sum() / len(df) * 100) if len(df) > 0 else 0,
            "avg_time": df["time_elapsed"].mean() if len(df) > 0 else 0,
            "by_algorithm": {},
        }

        # Statistics by algorithm
        for algo in df["algorithm"].unique():
            algo_df = df[df["algorithm"] == algo]
            stats["by_algorithm"][algo] = {
                "count": len(algo_df),
                "success_rate": (algo_df["success"].sum() / len(algo_df) * 100),
                "avg_time": algo_df["time_elapsed"].mean(),
            }

        return stats
