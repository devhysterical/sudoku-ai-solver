"""
Benchmark script to compare performance of all solvers
"""

import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.solvers import (
    backtracking,
    logic_solver,
    hybrid,
    dlx,
)

# Test puzzles of different difficulties
TEST_PUZZLES = {
    "easy": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "medium": [
        [0, 0, 0, 6, 0, 0, 4, 0, 0],
        [7, 0, 0, 0, 0, 3, 6, 0, 0],
        [0, 0, 0, 0, 9, 1, 0, 8, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 0, 1, 8, 0, 0, 0, 3],
        [0, 0, 0, 3, 0, 6, 0, 4, 5],
        [0, 4, 0, 2, 0, 0, 0, 6, 0],
        [9, 0, 3, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 1, 0, 0],
    ],
    "hard": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 0, 8, 5],
        [0, 0, 1, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 5, 0, 7, 0, 0, 0],
        [0, 0, 4, 0, 0, 0, 1, 0, 0],
        [0, 9, 0, 0, 0, 0, 0, 0, 0],
        [5, 0, 0, 0, 0, 0, 0, 7, 3],
        [0, 0, 2, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 4, 0, 0, 0, 9],
    ],
}


def benchmark_solver(name, solver_func, puzzle, runs=3):
    """Benchmark a single solver"""
    times = []
    steps_count = None
    success = False

    for _ in range(runs):
        start = time.perf_counter()
        try:
            result, steps = solver_func(puzzle)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

            if result is not None:
                success = True
                if steps_count is None:
                    steps_count = len(steps)
        except Exception as e:
            print(f"  ❌ Error in {name}: {str(e)}")
            return None

    if not times:
        return None

    return {
        "name": name,
        "success": success,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "steps": steps_count,
    }


def run_benchmark():
    """Run comprehensive benchmark"""
    print("=" * 80)
    print("SUDOKU SOLVER BENCHMARK")
    print("=" * 80)

    # Import optimized solvers (may fail if dependencies not installed)
    optimized_solvers = {}

    try:
        from ai.solvers import optimized_backtracking

        optimized_solvers["Optimized Backtracking"] = optimized_backtracking.solve
    except ImportError as e:
        print(f"⚠️  Optimized Backtracking not available: {e}")

    try:
        from ai.solvers import optimized_logic

        optimized_solvers["Optimized Logic"] = optimized_logic.solve
    except ImportError as e:
        print(f"⚠️  Optimized Logic not available: {e}")

    try:
        from ai.solvers import ortools_solver

        optimized_solvers["OR-Tools"] = ortools_solver.solve
    except ImportError as e:
        print(f"⚠️  OR-Tools not available: {e}")

    # Original solvers
    solvers = {
        "Backtracking": backtracking.solve,
        "Logic Solver": logic_solver.solve,
        "Hybrid": hybrid.solve,
        "DLX": dlx.solve,
    }

    # Combine all solvers
    all_solvers = {**solvers, **optimized_solvers}

    for difficulty, puzzle in TEST_PUZZLES.items():
        print(f"\n{'='*80}")
        print(f"Testing {difficulty.upper()} puzzle")
        print(f"{'='*80}\n")

        results = []

        for name, solver_func in all_solvers.items():
            print(f"Running {name}...", end=" ")
            result = benchmark_solver(name, solver_func, puzzle)

            if result:
                results.append(result)
                print(f"✅ {result['avg_time']*1000:.2f}ms (avg)")
            else:
                print("❌ Failed")

        # Sort by average time
        results.sort(key=lambda x: x["avg_time"])

        print(f"\n{'─'*80}")
        print("RANKING:")
        print(f"{'─'*80}")
        print(
            f"{'Rank':<6} {'Solver':<30} {'Avg Time':<15} {'Min Time':<15} {'Steps':<10}"
        )
        print(f"{'─'*80}")

        for i, result in enumerate(results, 1):
            speedup = ""
            if i > 1:
                speedup = f"({results[0]['avg_time'] / result['avg_time']:.2f}x slower)"
            elif i == 1:
                speedup = "⚡ FASTEST"

            print(
                f"{i:<6} {result['name']:<30} {result['avg_time']*1000:>10.2f}ms   "
                f"{result['min_time']*1000:>10.2f}ms   {result['steps']:<10} {speedup}"
            )

        print(f"{'─'*80}\n")

    print(f"\n{'='*80}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    run_benchmark()
