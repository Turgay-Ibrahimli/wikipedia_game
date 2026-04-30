#!/usr/bin/env python3
# Quick tests for cache_manager without full precomputation

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cache_manager import (
    is_pair_precomputed, 
    get_precompute_status,
    _load_precomputed_cache,
    _save_precomputed_cache,
    PRECOMPUTE_CACHE
)
import json

print("=" * 70)
print("QUICK CACHE_MANAGER TESTS")
print("=" * 70)

# Test 1: Load empty cache
print("\n[TEST 1] Loading cache...")
cache = _load_precomputed_cache()
print(f"✓ Cache loaded: {type(cache)} with {len(cache)} entries")

# Test 2: Check precomputed status for a random pair
print("\n[TEST 2] Check if random pair is precomputed...")
is_precomp = is_pair_precomputed("Test→Pair", "Not→Real")
print(f"✓ is_pair_precomputed() works: returned {is_precomp}")

# Test 3: Get precompute status
print("\n[TEST 3] Get precompute status...")
status = get_precompute_status()
print(f"Status:\n{status}")

# Test 4: Save and reload cache
print("\n[TEST 4] Test save/load cycle...")
test_cache = {
    "Python→Guido": {
        "complete": True,
        "nodes_count": 150,
        "api_calls": 50,
        "time_seconds": 45.3,
        "timestamp": 1234567890
    }
}
_save_precomputed_cache(test_cache)
reloaded = _load_precomputed_cache()
assert "Python→Guido" in reloaded, "Cache save/load failed"
assert reloaded["Python→Guido"]["nodes_count"] == 150, "Data corrupted"
print(f"✓ Saved test data and reloaded successfully")

# Test 5: Verify cache file exists and is valid JSON
print("\n[TEST 5] Verify cache file format...")
if os.path.exists(PRECOMPUTE_CACHE):
    with open(PRECOMPUTE_CACHE, 'r') as f:
        data = json.load(f)
    print(f"✓ Cache file is valid JSON with {len(data)} entries")
else:
    print(f"⚠ Cache file doesn't exist yet (normal if first run)")

# Test 6: Check is_pair_precomputed with saved data
print("\n[TEST 6] Check is_pair_precomputed with saved data...")
is_precomp = is_pair_precomputed("Python", "Guido")
print(f"✓ is_pair_precomputed('Python', 'Guido') = {is_precomp}")

print("\n" + "=" * 70)
print("ALL QUICK TESTS PASSED ✓")
print("=" * 70)
