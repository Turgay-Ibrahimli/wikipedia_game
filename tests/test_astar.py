# tests/test_astar.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from search.greedy import greedy
from search.astar import astar

graph = WikiGraph()

test_pairs = [
    ("Python (programming language)", "Guido van Rossum"),
    ("Python (programming language)", "Alan Turing"),
    ("Python (programming language)", "Napoleon"),
]

print("=" * 60)
print("Greedy vs A* — same pairs, same cache")
print("=" * 60)

for source, target in test_pairs:
    print(f"\n--- {source} -> {target} ---")

    g_result = greedy(source, target, graph, max_nodes=500)
    a_result = astar(source, target, graph, max_nodes=500)

    for label, result in [("Greedy", g_result), ("A*    ", a_result)]:
        if result.path:
            print(f"  {label}  {result.path_length} hops | {result.nodes_expanded} expanded | {result.time_taken}s")
            print(f"          {' -> '.join(result.path)}")
        else:
            print(f"  {label}  status={result.status} | {result.nodes_expanded} expanded | {result.time_taken}s")

graph.save_cache()