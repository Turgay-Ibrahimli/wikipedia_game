# Wikipedia Game — Setup Guide
# The final run is recommended by the part 8 UI 8. (Optional) Run the Web UI 
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
cd wikipedia_game
uv venv
cd ..
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
.\.venv\Scripts\Activate.ps1
```

If you created the venv inside `wikipedia_game/` (the `uv` commands above do this), activate it from the repo root with:
```powershell
.\wikipedia_game\.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
source .venv/bin/activate
```

If you created the venv inside `wikipedia_game/`, activate it from the repo root with:
```bash
source wikipedia_game/.venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

---

## 5. Install Dependencies

### With uv
```bash
# Run from the directory that contains `pyproject.toml`
cd wikipedia_game
uv sync
cd ..
```

### With pip
```bash
pip install -r wikipedia_game/requirements.txt
```

---

## 6. Run a Search

### Single search (interactive)
```bash
python wikipedia_game/main.py --source "Python (programming language)" --target "Napoleon" --algorithm greedy
```

Available algorithms: `bfs`, `dfs`, `greedy`, `astar`

### Run full experiments
```bash
python wikipedia_game/main.py --experiments --all-algorithms
```

Results will be saved to `results/results.csv`.

---

## 7. Visualize Results

```bash
python wikipedia_game/visualize.py
```

Charts will be saved to `results/`.

---

## 8. (Optional) Run the Web UI 

This repo includes a small Flask app in `wikipedia_game/server/app.py`.

### Install server deps

With pip:

```bash
pip install -r wikipedia_game/requirements-server.txt
```

With uv:

```bash
cd wikipedia_game
uv sync --extra server
cd ..
```

### Start the server

```bash
python wikipedia_game/server/app.py
```

Then open `http://127.0.0.1:5000/`.

---

## Notes

- On first run, the program will fetch Wikipedia pages and compute embeddings — this is slow but only happens once. Results are cached in `cache/`.
- Subsequent runs will be significantly faster as everything is read from cache.
- The `sentence-transformers` model (`all-MiniLM-L6-v2`) will be downloaded automatically on first run (~90MB).
- If you see connection/rate-limit errors, set `WIKIPEDIA_USER_AGENT` to a real contact string (e.g. `WikipediaGame/1.0 (email: you@example.com)`) and rerun.
