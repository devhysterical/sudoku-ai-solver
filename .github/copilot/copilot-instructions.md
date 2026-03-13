# 🤖 Copilot Instructions for Sudoku Web Project

## 🎯 Mục tiêu Dự án

Đây là một dự án ứng dụng web Sudoku sử dụng **FastAPI** cho Backend và **HTML/CSS/JavaScript thuần** cho Frontend (Không dùng framework). Dự án tập trung vào việc triển khai nhiều thuật toán giải Sudoku khác nhau (Backtracking, Logic Solver, Hybrid, DLX) và cung cấp một giao diện chơi game thân thiện với tính năng **animation các bước giải** của AI.

## 💡 Ngôn ngữ và Công nghệ

- **Backend:** Python, FastAPI, Pandas, Jinja2
- **Frontend:** HTML5, CSS3, ES6 (JavaScript thuần)
- **Dữ liệu:** CSV (puzzles.csv, solver_history.csv)

## ✨ Yêu cầu về Phong cách Code

1.  **Python:**
    - Tuân thủ **PEP 8**.
    - Sử dụng type hints đầy đủ cho các hàm và biến.
    - Sử dụng Docstrings (Google style hoặc reST style) cho các hàm phức tạp, đặc biệt là các hàm solver.
    - Các hàm utility phải được đặt trong thư mục `utils/` hoặc `ai/utils/`.
2.  **FastAPI:**
    - Sử dụng `Depends` và `BackgroundTasks` nếu cần thiết.
    - Trả về chuẩn JSON (camelCase cho JS, snake_case cho Python).
    - Sử dụng Pydantic cho request/response models của các API phức tạp.
3.  **JavaScript:**
    - Sử dụng **async/await** cho các lời gọi API.
    - Sử dụng ES6+ features.
    - Thao tác DOM phải rõ ràng, tránh inline styles/scripts.

## 🧩 Cấu trúc Code và Tên File Quan trọng

- **API Solvers:** Các file trong `ai/solvers/` phải có một hàm **public** duy nhất là `solve(board: list[list[int]]) -> tuple[list[list[int]], list[dict]]` trả về bảng đã giải và danh sách các bước (`steps`).
- **Puzzle Board Format:** Luôn là một list 2D (9x9) các số nguyên, với `0` đại diện cho ô trống.
- **Steps Format (cho animation):** Mỗi bước là một dictionary: `{'row': int, 'col': int, 'value': int, 'action': str}`. `action` có thể là 'fill', 'highlight', 'clear'.

## 🔒 Quy tắc Cấm

- Không được sử dụng thư viện UI/JS framework (như React, Vue, jQuery, etc.).
- Không được dùng database khác ngoài file CSV đã yêu cầu.
- Không được dùng thư viện giải Sudoku có sẵn (phải tự viết các thuật toán).

## Quy tắc phản hồi bắt buộc

- Ngôn ngữ phản hồi: Tiếng Việt
- Tuân thủ thiết kế. Mọi phản hồi phải tuân thủ tuyệt đối File Detailed Design này:

* tuân thủ cấu trúc folder
* tuân thủ phương thức API
* tuân thủ định dạng dữ liệu
* tuân thủ công nghệ cho phép
* không đề xuất framework ngoài phạm vi
* không thay đổi yêu cầu project

## Tích hợp AG Kit

- Quy tắc AG Kit đã được bridge sang định dạng Copilot tại `.github/instructions/ag-kit-bridge.instructions.md`.
- Ưu tiên áp dụng file bridge này khi làm việc trên mã nguồn để đảm bảo Copilot hiểu đúng conventions của dự án.
