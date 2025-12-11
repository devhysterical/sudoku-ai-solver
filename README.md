# 🧩 Sudoku AI Solver

Ứng dụng web Sudoku với AI solver sử dụng FastAPI và vanilla JavaScript.

## 🚀 Tính năng

- ✅ 4 thuật toán AI: Backtracking, Logic Solver, Hybrid, DLX
- 🎬 Animation hiển thị từng bước giải
- 🎮 Giao diện chơi game thân thiện
- 📊 Lưu lịch sử giải puzzle

## 🛠️ Công nghệ

- **Backend:** FastAPI, Python 3.10+
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Data:** CSV files

## 📦 Cài đặt

```bash
# Clone repository
git clone https://github.com/devhysterical/sudoku-ai-solver.git
cd sudoku-ai-solver

# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
uvicorn main:app --reload
```

## 🎯 Sử dụng

Truy cập: `http://localhost:8000`

## 📂 Cấu trúc Project

```
sudoku-ai-solver/
├── ai/
│   ├── solvers/          # AI solver algorithms
│   └── utils/            # AI utilities
├── data/                 # CSV data files
├── static/
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
├── templates/            # HTML templates
├── utils/               # General utilities
└── main.py              # FastAPI application
```

## 📝 License

MIT License
