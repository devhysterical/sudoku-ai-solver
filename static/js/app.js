/**
 * Sudoku AI Solver - Main Application
 * Vanilla JavaScript implementation
 */

// Application state
const state = {
  board: Array(9)
    .fill(null)
    .map(() => Array(9).fill(0)),
  originalBoard: null,
  isAnimating: false,
  isStopped: false,
  currentStep: 0,
  steps: [],
  animationSpeed: 50,
  selectedCell: null, // Track selected cell for keyboard input
};

// DOM Elements
let boardElement;
let statusElement;
let timeElement;
let stepsElement;
let cells = [];

/**
 * Initialize application
 */
document.addEventListener("DOMContentLoaded", () => {
  initializeDOM();
  createBoard();
  attachEventListeners();
  console.log("Sudoku AI Solver initialized");
});

/**
 * Initialize DOM element references
 */
function initializeDOM() {
  boardElement = document.getElementById("sudoku-board");
  statusElement = document.getElementById("status");
  timeElement = document.getElementById("time");
  stepsElement = document.getElementById("steps");
}

/**
 * Create Sudoku board UI
 */
function createBoard() {
  boardElement.innerHTML = "";
  cells = [];

  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = i;
      cell.dataset.col = j;
      cell.textContent = "";
      cell.tabIndex = 0; // Make cell focusable

      // Select cell on click
      cell.addEventListener("click", () => selectCell(i, j));

      boardElement.appendChild(cell);
      cells.push(cell);
    }
  }
}

/**
 * Select cell for keyboard input
 */
function selectCell(row, col) {
  if (state.isAnimating) return;

  const cell = getCellElement(row, col);
  if (cell.classList.contains("fixed")) return;

  // Remove previous selection
  if (state.selectedCell) {
    const prevCell = getCellElement(
      state.selectedCell.row,
      state.selectedCell.col
    );
    prevCell.classList.remove("selected");
  }

  // Set new selection
  state.selectedCell = { row, col };
  cell.classList.add("selected");
  cell.focus();
}

/**
 * Handle keyboard input for selected cell
 */
function handleKeyboardInput(event) {
  if (state.isAnimating || !state.selectedCell) return;

  const { row, col } = state.selectedCell;
  const cell = getCellElement(row, col);

  if (cell.classList.contains("fixed")) return;

  // Handle number keys (1-9) and 0/Delete/Backspace for clearing
  if (event.key >= "1" && event.key <= "9") {
    const value = parseInt(event.key);
    state.board[row][col] = value;
    updateCell(row, col, value);
  } else if (
    event.key === "0" ||
    event.key === "Delete" ||
    event.key === "Backspace"
  ) {
    state.board[row][col] = 0;
    updateCell(row, col, 0);
  } else if (
    event.key === "ArrowUp" ||
    event.key === "ArrowDown" ||
    event.key === "ArrowLeft" ||
    event.key === "ArrowRight"
  ) {
    // Navigate with arrow keys
    handleArrowNavigation(event.key);
    event.preventDefault();
  }
}

/**
 * Handle arrow key navigation
 */
function handleArrowNavigation(key) {
  if (!state.selectedCell) return;

  let { row, col } = state.selectedCell;

  switch (key) {
    case "ArrowUp":
      row = Math.max(0, row - 1);
      break;
    case "ArrowDown":
      row = Math.min(8, row + 1);
      break;
    case "ArrowLeft":
      col = Math.max(0, col - 1);
      break;
    case "ArrowRight":
      col = Math.min(8, col + 1);
      break;
  }

  selectCell(row, col);
}

/**
 * Get cell element by coordinates
 */
function getCellElement(row, col) {
  return cells[row * 9 + col];
}

/**
 * Update cell display
 */
function updateCell(row, col, value, animate = false) {
  const cell = getCellElement(row, col);
  cell.textContent = value === 0 ? "" : value;

  if (animate) {
    cell.classList.add("solving");
    setTimeout(() => cell.classList.remove("solving"), 500);
  }
}

/**
 * Attach event listeners to buttons
 */
function attachEventListeners() {
  document
    .getElementById("btnGenerate")
    .addEventListener("click", generatePuzzle);
  document.getElementById("btnSolve").addEventListener("click", solvePuzzle);
  document.getElementById("btnStop").addEventListener("click", stopSolving);
  document.getElementById("btnClear").addEventListener("click", clearBoard);
  document
    .getElementById("btnValidate")
    .addEventListener("click", validateBoard);

  // Add keyboard event listener
  document.addEventListener("keydown", handleKeyboardInput);

  document
    .getElementById("btnLoadHistory")
    .addEventListener("click", loadHistory);
  document.getElementById("speed").addEventListener("change", (e) => {
    state.animationSpeed = parseInt(e.target.value);
  });
}

/**
 * Generate new puzzle
 */
async function generatePuzzle() {
  try {
    setStatus("Đang tạo puzzle...", "info");
    disableButtons(true);

    const difficulty = document.getElementById("difficulty").value;

    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ difficulty }),
    });

    if (!response.ok) throw new Error("Failed to generate puzzle");

    const data = await response.json();

    state.board = data.board;
    state.originalBoard = JSON.parse(JSON.stringify(data.board));

    displayBoard(state.board, true);
    setStatus("Puzzle mới đã được tạo!", "success");
    updateStats(0, 0);
  } catch (error) {
    console.error("Error generating puzzle:", error);
    setStatus("Lỗi khi tạo puzzle", "error");
  } finally {
    disableButtons(false);
  }
}

/**
 * Solve puzzle using AI
 */
async function solvePuzzle() {
  if (state.isAnimating) {
    setStatus("Đang giải puzzle...", "info");
    return;
  }

  try {
    // Hiển thị feedback ngay lập tức
    setStatus("⏳ Đang tính toán...", "info");
    disableButtons(true);
    showStopButton(true);
    state.isAnimating = true;
    state.isStopped = false;

    // Force UI update
    await sleep(10);

    const algorithm = document.getElementById("algorithm").value;
    const startTime = performance.now();

    const response = await fetch("/api/solve", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        board: state.board,
        algorithm: algorithm,
      }),
    });

    if (!response.ok) throw new Error("Failed to solve puzzle");

    const data = await response.json();

    if (!data.success) {
      setStatus("Không tìm thấy lời giải", "error");
      state.isAnimating = false;
      disableButtons(false);
      showStopButton(false);
      return;
    }

    setStatus("🎬 Đang giải...", "info");

    // Animate solving steps
    state.steps = data.steps;
    const completed = await animateSteps(data.steps);

    if (!completed) {
      setStatus("⏸️ Đã dừng giải", "warning");
      state.isAnimating = false;
      disableButtons(false);
      showStopButton(false);
      return;
    }

    const elapsed = (performance.now() - startTime) / 1000;
    setStatus("Đã giải thành công!", "success");
    updateStats(elapsed, data.steps.length);

    state.board = data.solved_board;
    displayBoard(state.board, false);
  } catch (error) {
    console.error("Error solving puzzle:", error);
    setStatus("Lỗi khi giải puzzle", "error");
  } finally {
    state.isAnimating = false;
    disableButtons(false);
    showStopButton(false);
  }
}

/**
 * Stop solving animation
 */
function stopSolving() {
  if (state.isAnimating) {
    state.isStopped = true;
    setStatus("⏸️ Đang dừng...", "warning");
  }
}

/**
 * Animate solving steps
 */
async function animateSteps(steps) {
  if (state.animationSpeed === 0) {
    // No animation - show final result
    for (const step of steps) {
      if (state.isStopped) return false;

      if (step.action === "fill") {
        state.board[step.row][step.col] = step.value;
        updateCell(step.row, step.col, step.value);
      } else if (step.action === "clear") {
        state.board[step.row][step.col] = 0;
        updateCell(step.row, step.col, 0);
      }
    }
    return true;
  }

  for (let i = 0; i < steps.length; i++) {
    // Check if stopped
    if (state.isStopped) {
      return false;
    }

    const step = steps[i];

    if (step.action === "fill") {
      state.board[step.row][step.col] = step.value;
      updateCell(step.row, step.col, step.value, true);
    } else if (step.action === "clear") {
      state.board[step.row][step.col] = 0;
      updateCell(step.row, step.col, 0);
    } else if (step.action === "highlight") {
      const cell = getCellElement(step.row, step.col);
      cell.classList.add("highlight");
      setTimeout(() => cell.classList.remove("highlight"), 500);
    }

    stepsElement.textContent = i + 1;

    // Wait for animation
    await sleep(state.animationSpeed);
  }

  return true;
}

/**
 * Clear board
 */
function clearBoard() {
  if (state.isAnimating) return;

  state.board = Array(9)
    .fill(null)
    .map(() => Array(9).fill(0));
  state.originalBoard = null;
  state.steps = [];

  displayBoard(state.board, false);
  setStatus("Bảng đã được xóa", "info");
  updateStats(0, 0);
}

/**
 * Validate current board
 */
async function validateBoard() {
  try {
    setStatus("Đang kiểm tra...", "info");

    const response = await fetch("/api/validate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ board: state.board }),
    });

    if (!response.ok) throw new Error("Failed to validate");

    const data = await response.json();

    // Clear previous errors
    cells.forEach((cell) => cell.classList.remove("error"));

    if (data.is_valid) {
      setStatus("Bảng hợp lệ!", "success");
    } else {
      setStatus(`Có ${data.errors.length} lỗi`, "error");

      // Highlight errors
      data.errors.forEach((error) => {
        if (error.row !== undefined && error.col !== undefined) {
          const cell = getCellElement(error.row, error.col);
          cell.classList.add("error");
        }
      });
    }
  } catch (error) {
    console.error("Error validating board:", error);
    setStatus("Lỗi khi kiểm tra", "error");
  }
}

/**
 * Load solving history
 */
async function loadHistory() {
  try {
    const response = await fetch("/api/history?limit=10");

    if (!response.ok) throw new Error("Failed to load history");

    const data = await response.json();

    displayHistory(data.history);
  } catch (error) {
    console.error("Error loading history:", error);
  }
}

/**
 * Display history entries
 */
function displayHistory(history) {
  const historyList = document.getElementById("history-list");
  historyList.innerHTML = "";

  if (history.length === 0) {
    historyList.innerHTML =
      '<p style="text-align: center; color: #7f8c8d;">Chưa có lịch sử</p>';
    return;
  }

  history.forEach((entry) => {
    const item = document.createElement("div");
    item.className = "history-item";

    const info = document.createElement("div");
    info.className = "history-info";

    const algorithm = document.createElement("div");
    algorithm.className = "history-algorithm";
    algorithm.textContent = entry.algorithm.toUpperCase();

    const time = document.createElement("div");
    time.className = "history-time";
    time.textContent = `${entry.time_elapsed.toFixed(3)}s - ${new Date(
      entry.timestamp
    ).toLocaleString("vi-VN")}`;

    info.appendChild(algorithm);
    info.appendChild(time);

    const status = document.createElement("div");
    status.className = `history-status ${entry.success ? "success" : "failed"}`;
    status.textContent = entry.success ? "Thành công" : "Thất bại";

    item.appendChild(info);
    item.appendChild(status);

    historyList.appendChild(item);
  });
}

/**
 * Display board on UI
 */
function displayBoard(board, markFixed = false) {
  // Clear selection when displaying new board
  state.selectedCell = null;

  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const cell = getCellElement(i, j);
      const value = board[i][j];

      cell.textContent = value === 0 ? "" : value;
      cell.classList.remove(
        "fixed",
        "filled",
        "error",
        "highlight",
        "selected"
      );

      if (markFixed && value !== 0) {
        cell.classList.add("fixed");
      } else if (value !== 0) {
        cell.classList.add("filled");
      }
    }
  }
}

/**
 * Update status message
 */
function setStatus(message, type = "info") {
  statusElement.textContent = message;
  statusElement.style.color =
    {
      info: "#3498db",
      success: "#2ecc71",
      error: "#e74c3c",
      warning: "#f39c12",
    }[type] || "#3498db";
}

/**
 * Update statistics display
 */
function updateStats(time, steps) {
  timeElement.textContent = `${time.toFixed(3)}s`;
  stepsElement.textContent = steps;
}

/**
 * Enable/disable control buttons
 */
function disableButtons(disabled) {
  const buttons = ["btnGenerate", "btnSolve", "btnClear", "btnValidate"];
  buttons.forEach((id) => {
    document.getElementById(id).disabled = disabled;
  });
}

/**
 * Show/hide stop button
 */
function showStopButton(show) {
  const btnStop = document.getElementById("btnStop");
  const btnSolve = document.getElementById("btnSolve");

  if (show) {
    btnStop.style.display = "inline-block";
    btnSolve.style.display = "none";
  } else {
    btnStop.style.display = "none";
    btnSolve.style.display = "inline-block";
  }
}

/**
 * Sleep utility for animation
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Export for potential module usage
export { state, generatePuzzle, solvePuzzle, clearBoard, validateBoard };
