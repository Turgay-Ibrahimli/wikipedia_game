#!/usr/bin/env python3
# Test precomputation on a single pair (faster than full batch)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from cache_manager import (
    precompute_page_pair,
    is_pair_precomputed,
    _load_precomputed_cache,
)
import time

print("=" * 70)
print("CACHE_MANAGER PRECOMPUTATION TEST")
print("=" * 70)

# Use a short pair to test quickly
source = "Python (programming language)"
target = "Computer science"

print(f"\nTest pair: {source} → {target}")
print(f"Note: This tests precomputation logic on a single pair")

# Check if already precomputed
already_precomputed = is_pair_precomputed(source, target)
print(f"\nAlready precomputed? {already_precomputed}")

if already_precomputed:
    print("\n✓ Pair is already in cache (skipping precomputation)")
    cache = _load_precomputed_cache()
    pair_key = f"{source}→{target}"
    if pair_key in cache:
        info = cache[pair_key]
        print(f"  Nodes cached: {info['nodes_count']}")
        print(f"  API calls: {info['api_calls']}")
        print(f"  Time taken: {info['time_seconds']:.1f}s")
else:
    print("\n⏳ Running precomputation on single pair (may take 1-5 minutes)...")
    graph = WikiGraph()
    
    start = time.time()
    nodes_count, elapsed = precompute_page_pair(source, target, graph, verbose=True)
    total_time = time.time() - start
    
    print(f"\nResults:")
    print(f"  Nodes cached: {nodes_count}")
    print(f"  Time taken: {elapsed:.1f}s")
    print(f"  Total time: {total_time:.1f}s")

print("\n" + "=" * 70)
print("TEST COMPLETE ✓")
print("=" * 70)
