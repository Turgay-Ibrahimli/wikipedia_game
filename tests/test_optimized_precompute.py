#!/usr/bin/env python3
# Test optimized precomputation with timeout

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from cache_manager import precompute_page_pair
import time

print("=" * 70)
print("TEST: Optimized Precomputation with Timeout")
print("=" * 70)

# Test a problematic pair that was hanging
graph = WikiGraph()

pair = ("Quantum mechanics", "Thermodynamics")
print(f"\nTesting pair: {pair[0]} → {pair[1]}")
print("(This pair is highly connected and was hanging before)")
print(f"Timeout: 120 seconds\n")

start = time.time()
nodes, elapsed = precompute_page_pair(pair[0], pair[1], graph, verbose=True, timeout=120)
total_time = time.time() - start

print(f"\n{'='*70}")
print(f"Results:")
print(f"  Nodes cached: {nodes}")
print(f"  Time: {elapsed:.1f}s")
print(f"  Total: {total_time:.1f}s")
print(f"{'='*70}\n")

if elapsed < 120:
    print("✓ Completed within timeout!")
else:
    print("⚠ Hit timeout limit (precomputation was too slow)")
