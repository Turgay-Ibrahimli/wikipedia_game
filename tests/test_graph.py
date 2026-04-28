# tests/test_graph.py (temporary, just to verify)
import os
import sys

# Allow running directly from repo root: `python wikipedia_game/tests/test_graph.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wiki_graph import WikiGraph

graph = WikiGraph()

neighbors = graph.get_neighbors("Python (programming language)")
print(f"Found {len(neighbors)} links")
print(neighbors[:10])  # Print first 10

graph.save_cache()
