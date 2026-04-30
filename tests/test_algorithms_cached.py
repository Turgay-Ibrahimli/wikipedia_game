#!/usr/bin/env python3
# Verify that algorithms work with existing cache

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from search.bfs import bfs
from search.dfs import dfs
from search.greedy import greedy
from search.astar import astar
from cache_manager import is_pair_precomputed, get_precompute_status
import time

print("=" * 70)
print("ALGORITHM TEST WITH CACHED DATA")
print("=" * 70)

print("\nPrecomputed Pairs Available:")
print(get_precompute_status())

# Use the precomputed pairs
test_pairs = [
    ("Python (programming language)", "Guido van Rossum"),
    ("Python (programming language)", "Computer science"),
]

graph = WikiGraph()

print("\nRunning algorithms on cached pairs...")
print("=" * 70)

for source, target in test_pairs:
    print(f"\nTest: {source} → {target}")
    print(f"Cache exists? {is_pair_precomputed(source, target)}")
    
    algorithms = {
        "BFS":    bfs,
        "DFS":    dfs,
        "Greedy": greedy,
        "A*":     astar,
    }
    
    for algo_name, algo_func in algorithms.items():
        start = time.time()
        result = algo_func(source, target, graph, max_nodes=500)
        elapsed = time.time() - start
        
        status = "✓" if result.path else "✗"
        path_info = f"{result.path_length}h" if result.path else result.status
        
        print(f"  {algo_name:8} {status} | {path_info:8} | {result.nodes_expanded:5} nodes | {elapsed:.2f}s")
        
        if result.path:
            print(f"           Path: {' → '.join(result.path[:3])}..." if len(result.path) > 3 else f"           Path: {' → '.join(result.path)}")

print("\n" + "=" * 70)
print("ALGORITHM TEST COMPLETE ✓")
print("=" * 70)

graph.save_cache()
