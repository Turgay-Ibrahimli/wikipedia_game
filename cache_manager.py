# cache_manager.py
# Pre-computes and stores node expansions to avoid cold-start delays
# Stores expanded nodes in JSON for instant cache warm-up on subsequent runs

import json
import os
import time
from wiki_graph import WikiGraph
from heuristic import get_embedding

PRECOMPUTE_CACHE = "cache/precomputed_nodes.json"

def _load_precomputed_cache():
    """Load the precomputed nodes cache from disk."""
    if not os.path.exists(PRECOMPUTE_CACHE):
        return {}
    
    try:
        with open(PRECOMPUTE_CACHE, 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_precomputed_cache(cache):
    """Save the precomputed nodes cache to disk."""
    os.makedirs(os.path.dirname(PRECOMPUTE_CACHE), exist_ok=True)
    with open(PRECOMPUTE_CACHE, 'w') as f:
        json.dump(cache, f, indent=2)

def precompute_page_pair(source, target, graph, verbose=True, timeout=120):
    """
    Pre-compute and cache all neighbors and embeddings for a source-target pair.
    
    This performs a BFS from source to find all nodes reachable within a reasonable
    depth, ensuring both neighbors and embeddings are cached before experiments run.
    
    Args:
        source: Starting page title
        target: Destination page title
        graph: WikiGraph instance
        verbose: Print progress messages
        timeout: Maximum time in seconds before stopping precomputation (default 120)
    
    Returns:
        Tuple of (nodes_precomputed, time_taken)
    """
    start_time = time.time()
    precomputed_cache = _load_precomputed_cache()
    
    # Check if this pair is already fully precomputed
    pair_key = f"{source}→{target}"
    if pair_key in precomputed_cache and precomputed_cache[pair_key].get("complete"):
        if verbose:
            print(f"✓ {pair_key} already precomputed")
        return precomputed_cache[pair_key]["nodes_count"], 0
    
    if verbose:
        print(f"⏳ Precomputing {pair_key}...")
    
    nodes_to_visit = set()
    visited = set()
    queue = [(source, 0)]  # (node, depth)
    max_depth = 2  # Reduced from 4 for faster precomputation
    nodes_fetched = 0
    
    # BFS to discover all nodes that might be expanded
    while queue and len(visited) < 1000:  # Reduced from 5000 for faster precomputation
        # Check timeout
        if time.time() - start_time > timeout:
            if verbose:
                print(f"  ⚠ Timeout after {timeout}s (explored {len(visited)} nodes)")
            break
        
        current, depth = queue.pop(0)
        
        if current in visited or depth > max_depth:
            continue
        
        visited.add(current)
        nodes_to_visit.add(current)
        
        # Get neighbors (this will use cache if available, else API)
        neighbors = graph.get_neighbors(current)
        nodes_fetched += 1
        
        # Early termination if we find target
        if target in neighbors:
            nodes_to_visit.add(target)
            if verbose and depth < max_depth:
                print(f"  ✓ Found target at depth {depth}")
        
        # Queue neighbors up to max depth, with reduced limit for speed
        if depth < max_depth:
            limit = 30 if depth == 0 else 20  # Fewer neighbors at each level
            for neighbor in neighbors[:limit]:  # Reduced from 100
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
    
    # Now ensure all discovered nodes have embeddings cached (but with timeout)
    if verbose:
        print(f"  Caching embeddings for {len(nodes_to_visit)} nodes...")
    
    embeddings_cached = 0
    for i, node in enumerate(nodes_to_visit):
        # Check timeout during embedding
        if time.time() - start_time > timeout:
            if verbose:
                print(f"  ⚠ Timeout during embedding ({embeddings_cached}/{len(nodes_to_visit)} cached)")
            break
        
        try:
            get_embedding(node, graph)  # This caches the embedding
            embeddings_cached += 1
            if verbose and (i + 1) % 50 == 0:
                print(f"    {i+1}/{len(nodes_to_visit)} embeddings cached...")
        except Exception as e:
            if verbose:
                print(f"  Warning: Failed to embed {node}: {e}")
    
    # Save progress to precomputed cache
    elapsed = time.time() - start_time
    precomputed_cache[pair_key] = {
        "complete": True,
        "nodes_count": len(nodes_to_visit),
        "api_calls": nodes_fetched,
        "time_seconds": elapsed,
        "timestamp": time.time()
    }
    _save_precomputed_cache(precomputed_cache)
    
    # Save updated caches to disk
    graph.save_cache()
    
    if verbose:
        print(f"✓ Precomputed {len(nodes_to_visit)} nodes in {elapsed:.1f}s")
    
    return len(nodes_to_visit), elapsed

def precompute_batch(page_pairs, graph, verbose=True, timeout_per_pair=120):
    """
    Pre-compute multiple page pairs at once.
    
    Args:
        page_pairs: List of (source, target) tuples
        graph: WikiGraph instance
        verbose: Print progress
        timeout_per_pair: Timeout in seconds per pair (default 120)
    
    Returns:
        List of (pair, nodes_count, time) tuples
    """
    results = []
    total_start = time.time()
    skipped = []
    
    for i, (source, target) in enumerate(page_pairs):
        print(f"\n[{i+1}/{len(page_pairs)}]", end=" ")
        try:
            nodes, elapsed = precompute_page_pair(source, target, graph, verbose=verbose, timeout=timeout_per_pair)
            results.append(((source, target), nodes, elapsed))
        except KeyboardInterrupt:
            print(f"\n⚠ Skipped by user")
            skipped.append((source, target))
        except Exception as e:
            print(f"\n✗ Error: {e}")
            skipped.append((source, target))
    
    total_elapsed = time.time() - total_start
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Precompute Complete:")
        for (source, target), nodes, elapsed in results:
            print(f"  {source:30} → {target:30} | {nodes:4d} nodes | {elapsed:6.1f}s")
        if skipped:
            print(f"\nSkipped {len(skipped)} pairs:")
            for source, target in skipped:
                print(f"  {source:30} → {target:30}")
        print(f"Total time: {total_elapsed:.1f}s")
        print(f"{'='*60}")
    
    return results

def is_pair_precomputed(source, target):
    """Check if a source-target pair has been precomputed."""
    precomputed_cache = _load_precomputed_cache()
    pair_key = f"{source}→{target}"
    return pair_key in precomputed_cache and precomputed_cache[pair_key].get("complete", False)

def get_precomputed_nodes(source, target, graph):
    """
    Get the set of nodes that have been precomputed/pre-expanded for a source-target pair.
    
    These are nodes whose neighbors have been cached (either from precomputation or 
    from previous searches). Returns the set of all cached node keys.
    
    Args:
        source: Source page title
        target: Target page title
        graph: WikiGraph instance
    
    Returns:
        Set of node titles that have been pre-expanded/cached
    """
    # Get all nodes that have cached neighbors
    precomputed_set = set()
    
    if hasattr(graph, 'links_cache') and graph.links_cache:
        precomputed_set = set(graph.links_cache.keys())
    
    return precomputed_set

def get_precompute_status():
    """Get a summary of all precomputed pairs."""
    precomputed_cache = _load_precomputed_cache()
    if not precomputed_cache:
        return "No precomputed pairs yet."
    
    status = "Precomputed Pairs:\n"
    for pair_key, info in precomputed_cache.items():
        if info.get("complete"):
            status += f"  ✓ {pair_key}: {info['nodes_count']} nodes in {info['time_seconds']:.1f}s\n"
    return status
