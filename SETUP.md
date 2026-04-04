# Wikipedia Game — Setup Guide

## Requirements
- Python 3.10+
- `uv` (recommended) or `pip`

---

## 1. Install a Package Manager

### Using uv (recommended)

**Windows**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Using pip (comes with Python)
If you have Python installed, pip is already available. Verify with:
```bash
pip --version
```
If not, download Python from https://python.org — pip is included.

---

## 2. Clone the Repository

```bash
git clone https://github.com/your-username/wikipedia_game.git
cd wikipedia_game
```

---

## 3. Create a Virtual Environment

### With uv
```bash
uv venv
```

### With pip

**Windows**
```powershell
python -m venv .venv
```

**macOS / Linux**
```bash
python3 -m venv .venv
```

---

## 4. Activate the Virtual Environment

### Windows
```powershell
.venv\Scripts\activate
```

### macOS / Linux
```bash
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

---

## 5. Install Dependencies

### With uv
```bash
uv sync
```

### With pip
```bash
pip install -r requirements.txt
```

---

## 6. Run a Search

### Single search (interactive)
```bash
python main.py --source "Python (programming language)" --target "Napoleon" --algorithm greedy
```

Available algorithms: `bfs`, `dfs`, `greedy`, `astar`

### Run full experiments
```bash
python main.py --experiments
```

Results will be saved to `results/results.csv`.

---

## 7. Visualize Results

```bash
python visualize.py
```

Charts will be saved to `results/`.

---

## Notes

- On first run, the program will fetch Wikipedia pages and compute embeddings — this is slow but only happens once. Results are cached in `cache/`.
- Subsequent runs will be significantly faster as everything is read from cache.
- The `sentence-transformers` model (`all-MiniLM-L6-v2`) will be downloaded automatically on first run (~90MB).
