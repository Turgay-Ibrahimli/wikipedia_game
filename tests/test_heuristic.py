# tests/test_heuristic.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from heuristic import h

graph = WikiGraph()
target = "Quantum mechanics"

pages = ["Physics", "Albert Einstein", "Cooking", "Napoleon", "Linear algebra"]

print(f"Heuristic scores against '{target}':\n")
for page in pages:
    score = h(page, target, graph)
    print(f"  {page}: {score:.4f}")