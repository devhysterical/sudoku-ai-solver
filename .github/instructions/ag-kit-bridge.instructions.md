---
description: "Use when working on Sudoku AI Solver codebase with AG Kit conventions (FastAPI backend, vanilla JS frontend, solver interface, CSV data)."
applyTo: "**/*.{py,js,html,css,md}"
---

# AG Kit Bridge Instructions (for GitHub Copilot)

## Scope
These instructions bridge project conventions from `.agent/` into GitHub Copilot-native instruction format.
Use these rules for all changes in this repository.

## Project Constraints
- Keep stack unchanged: FastAPI + HTML/CSS/vanilla JavaScript + CSV files.
- Do not introduce UI frameworks (React/Vue/jQuery) or non-CSV database layers.
- Keep existing API and folder structure unless explicitly requested.

## Backend Rules
- Follow PEP 8 and keep type hints for public functions.
- Use Pydantic models for request/response contracts.
- Keep error handling explicit: preserve `HTTPException`; only map unexpected errors to 500.
- Solver contract in `ai/solvers/`: public function signature should remain
  `solve(board: list[list[int]]) -> tuple[list[list[int]] | None, list[dict]]`.

## Frontend Rules
- Keep vanilla JS style (async/await for API calls).
- Keep board data format as 9x9 int matrix; `0` means empty.
- Keep step format for animation:
  `{"row": int, "col": int, "value": int, "action": "fill"|"highlight"|"clear"}`.

## Data and Security Rules
- Prefer safe parsing (`ast.literal_eval` / JSON parsing), never use `eval` for persisted data.
- Validate input shape and bounds for board-related endpoints.
- Keep CORS environment-driven for deploy flexibility.

## Quality Rules
- Prefer minimal, targeted edits over broad refactors.
- Update docs when behavior or exposed options change.
- Add or update tests for logic and API changes when possible.

## AG Kit Reference (Optional)
When needed, consult:
- `.agent/rules/copilot-instructions.md`
- `.agent/ARCHITECTURE.md`
- `.agent/skills/`

These are reference sources; this file is the Copilot-native execution layer.
