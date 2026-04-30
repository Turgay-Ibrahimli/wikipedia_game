#!/usr/bin/env python3
# test_cache_manager.py — Quick test of cache_manager functionality

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_graph import WikiGraph
from cache_manager import is_pair_precomputed, get_precompute_status

def test_cache_manager():
    print("Testing cache_manager.py...")
    print("=" * 60)
    
    # Test 1: Check precompute status
    print("\n1. Current precompute status:")
    print(get_precompute_status())
    
    # Test 2: Check if pairs are precomputed
    test_pairs = [
        ("Python (programming language)", "Guido van Rossum"),
        ("Python (programming language)", "Napoleon"),
    ]
    
    print("\n2. Precompute status for specific pairs:")
    for source, target in test_pairs:
        is_precomputed = is_pair_precomputed(source, target)
        status = "✓ Precomputed" if is_precomputed else "✗ Not precomputed"
        print(f"   {source:30} → {target:30} {status}")
    
    print("\n3. Testing imports:")
    try:
        from cache_manager import precompute_page_pair, precompute_batch
        print("   ✓ cache_manager functions imported successfully")
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        return False
    
    print("\n4. Testing WikiGraph integration:")
    try:
        graph = WikiGraph()
        print(f"   ✓ WikiGraph loaded successfully")
        print(f"   ✓ Cached links: {len(graph.cache)} pages")
    except Exception as e:
        print(f"   ✗ WikiGraph error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Cache manager test complete!")
    print("\nNext steps:")
    print("  1. Run: python main.py precompute")
    print("     (pre-computes all pairs in cache/precompute_pairs.csv)")
    print("\n  2. Then run: python main.py status")
    print("     (shows which pairs are cached)")
    print("\n  3. Run searches: python main.py search <source> <target>")
    print("     (instant queries with warm cache)")
    
    return True

if __name__ == "__main__":
    success = test_cache_manager()
    sys.exit(0 if success else 1)
