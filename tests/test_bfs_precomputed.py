#!/usr/bin/env python3
# Test: BFS with precomputed nodes tracking

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from search.bfs import bfs
from cache_manager import get_precomputed_nodes
import json

print("=" * 70)
print("TEST: BFS with Precomputed Nodes Tracking")
print("=" * 70)

graph = WikiGraph()

# Test a cached pair
source = "Cristiano Ronaldo"
target = "Elon Musk"

print(f"\nTest pair: {source} → {target}\n")

# Check cache before search
precomputed = get_precomputed_nodes(source, target, graph)
print(f"Precomputed nodes in cache: {len(precomputed)}")
if precomputed:
    print(f"Sample cached nodes: {list(precomputed)[:5]}\n")

# Run BFS
print(f"Running BFS...")
result = bfs(source, target, graph, max_nodes=500)

# Display results
print(f"\n--- BFS Results ---")
print(f"Path found: {bool(result.path)}")
if result.path:
    print(f"Path: {' → '.join(result.path)}")
    print(f"Hops: {result.path_length}")

print(f"\nNodes expanded: {result.nodes_expanded}")
print(f"Precomputed cache hits: {result.precomputed_hits}")
print(f"Cache hit rate: {result.precomputed_hits / result.nodes_expanded * 100:.1f}%")
print(f"Time taken: {result.time_taken:.4f}s")

print("\n" + "=" * 70)
print("TEST COMPLETE ✓")
print("=" * 70)
