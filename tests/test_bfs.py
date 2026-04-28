# tests/test_bfs.py
import os
import sys

# Allow running directly from repo root: `python wikipedia_game/tests/test_bfs.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wiki_graph import WikiGraph
from search.bfs import bfs

graph = WikiGraph()

# First check if Guido is a direct link
neighbors = graph.get_neighbors("Python (programming language)")
print("Guido in neighbors?", "Guido van Rossum" in neighbors)

result = bfs("Python (programming language)", "Guido van Rossum", graph, max_nodes=10000)

if result.path:
    print(f"Path: {' -> '.join(result.path)}")
    print(f"Length: {result.path_length}")
else:
    print(f"Status: {result.status}")

print(f"Nodes expanded: {result.nodes_expanded}")
print(f"Time: {result.time_taken}s")

graph.save_cache()
