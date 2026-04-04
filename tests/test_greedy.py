# tests/test_greedy.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from search.greedy import greedy

graph = WikiGraph()

test_pairs = [
    ("Python (programming language)", "Guido van Rossum"),
    ("Python (programming language)", "Alan Turing"),
    ("Python (programming language)", "Napoleon"),
]

for source, target in test_pairs:
    print(f"\n{source} -> {target}")
    result = greedy(source, target, graph, max_nodes=500)
    if result.path:
        print(f"Path: {' -> '.join(result.path)}")
        print(f"Length: {result.path_length}")
    else:
        print(f"Status: {result.status}")
    print(f"Nodes expanded: {result.nodes_expanded}")
    print(f"Time: {result.time_taken}s")

graph.save_cache()