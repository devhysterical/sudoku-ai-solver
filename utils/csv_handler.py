"""
CSV file handler for puzzles and history
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
import random
import uuid
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.generator import generate_puzzle


class CSVHandler:
    """Handle CSV operations for puzzles and history"""

    def __init__(self):
        self.data_dir = "data"
        self.puzzles_file = os.path.join(self.data_dir, "puzzles.csv")
        self.history_file = os.path.join(self.data_dir, "solver_history.csv")
        self._initialize_files()

    def _initialize_files(self):
        """Initialize CSV files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize puzzles.csv
        if not os.path.exists(self.puzzles_file):
            df = pd.DataFrame(columns=["id", "difficulty", "board", "solution"])
            df.to_csv(self.puzzles_file, index=False)
            self._generate_sample_puzzles()

        # Initialize solver_history.csv
        if not os.path.exists(self.history_file):
            df = pd.DataFrame(
                columns=[
                    "timestamp",
                    "puzzle_id",
                    "algorithm",
                    "difficulty",
                    "time_elapsed",
                    "success",
                ]
            )
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
            {"id": str(uuid.uuid4()), "difficulty": "easy", "board": str(easy_puzzle)},
            {
                "id": str(uuid.uuid4()),
                "difficulty": "medium",
                "board": str(medium_puzzle),
            },
            {"id": str(uuid.uuid4()), "difficulty": "hard", "board": str(hard_puzzle)},
        ]

        df = pd.DataFrame(puzzles)
        df.to_csv(self.puzzles_file, index=False)

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
            df = pd.read_csv(self.puzzles_file)

            # Filter by difficulty
            puzzles = df[df["difficulty"] == difficulty]

            if len(puzzles) == 0:
                # Fallback to any puzzle
                puzzles = df

            # Select random puzzle
            puzzle = puzzles.sample(n=1).iloc[0]

            # Parse board string to list
            board = eval(puzzle["board"])

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

        df = pd.DataFrame([entry])

        # Append to existing file
        if os.path.exists(self.puzzles_file):
            df.to_csv(self.puzzles_file, mode="a", header=False, index=False)
        else:
            df.to_csv(self.puzzles_file, index=False)

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

        df = pd.DataFrame([entry])

        # Append to existing file
        if os.path.exists(self.history_file):
            df.to_csv(self.history_file, mode="a", header=False, index=False)
        else:
            df.to_csv(self.history_file, index=False)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get solving history

        Args:
            limit: Maximum number of entries

        Returns:
            List of history entries
        """
        if not os.path.exists(self.history_file):
            return []

        df = pd.read_csv(self.history_file)

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
        if not os.path.exists(self.history_file):
            return {
                "total_solves": 0,
                "success_rate": 0,
                "avg_time": 0,
                "by_algorithm": {},
            }

        df = pd.read_csv(self.history_file)

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
