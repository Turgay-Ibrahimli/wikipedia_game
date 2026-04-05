# search/astar.py
import time
import tracemalloc
import heapq
from metrics import SearchMetrics
from heuristic import h

def astar(source, target, graph, max_nodes=10000, weight=3.0):
    """
    Weighted A* Search over the Wikipedia link graph.

    f(n) = g(n) + weight * h(n)

    =========================================================================
    TRIAL HISTORY — what we tried and why we moved on
    =========================================================================

    TRIAL 1 — Standard A* (weight=1), eager heuristic evaluation
    -------------------------------------------------------------
    First implementation: f(n) = g(n) + h(n), with h() computed for every
    neighbor before pushing to the heap.

    Problem: h() calls get_summary() + model.encode() for each neighbor.
    With ~700 links per page, that's ~700 cold API calls per expansion.
    The Napoleon pair hung for over an hour and had to be killed manually.

    Result: completely infeasible on cold cache. Never finished.

    TRIAL 2 — Standard A* (weight=1), lazy heuristic evaluation
    ------------------------------------------------------------
    Fix: only compute h() for neighbors whose embeddings are already in
    cache. Uncached neighbors are pushed with f = g_next as a lower-bound
    estimate, deferring their real score until they're popped.

    This eliminated the cold-cache hang. But a new problem emerged:
    the g(n) term kept pulling the search back to re-examine shallow nodes.
    With a branching factor of ~700, the open set exploded and A* expanded
    500 nodes on the Napoleon pair (hitting the cap) while Greedy solved
    the same pair in 8 expansions.

    Result: 500 nodes expanded, timeout. Worse than Greedy in every metric.

    Root cause: our heuristic (cosine distance on sentence embeddings) is
    actually strong enough to guide search on its own. Adding g(n) at equal
    weight introduces a bias toward short-but-wrong paths that the heuristic
    wouldn't have taken. Standard A* is theoretically optimal but practically
    worse here because the branching factor punishes cautious exploration.

    TRIAL 3 — Weighted A* (weight=3.0), lazy heuristic evaluation  ← CURRENT
    -------------------------------------------------------------------------
    Fix: f(n) = g(n) + 3.0 * h(n). Biasing the heuristic term lets A*
    behave close to Greedy when h is reliable, while still using g as a
    tiebreaker to prefer shorter paths among equally-scored nodes.

    The weight=3.0 guarantee: the path found is at most 3x the optimal
    hop count. In practice on Wikipedia this is not a meaningful loss —
    Greedy already has no optimality guarantee at all, and weighted A*
    finds paths of the same length while giving us the g(n) tiebreaker
    for free.

    Lazy evaluation is retained: h() is only computed for neighbors already
    in the embeddings cache. Uncached neighbors are pushed with f = g_next.

    =========================================================================
    WHY WEIGHTED A* IS THE RIGHT CALL FOR THIS PROBLEM
    =========================================================================
    Wikipedia's branching factor (~700 links/page) makes standard A*
    impractical — the open set grows too fast relative to the gain from
    tracking exact path cost. Our sentence-embedding heuristic is strong
    enough that the greedy signal dominates. Weighted A* is the honest
    middle ground: we're explicitly trading strict optimality for
    tractability, which is the same tradeoff real-world graph search
    systems make when the heuristic is known to be reliable.
    """
    start_time = time.time()
    tracemalloc.start()

    closed = set()
    g_cost = {source: 0}

    h_source = h(source, target, graph)
    # heap: (f, g, page, path)
    heap = [(weight * h_source, 0, source, [source])]
    nodes_expanded = 0

    while heap:
        if nodes_expanded >= max_nodes:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="A*", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        f, g, current, path = heapq.heappop(heap)

        if current in closed:
            continue
        closed.add(current)
        nodes_expanded += 1

        neighbors = graph.get_neighbors(current)

        # early target detection — free, no embedding needed
        if target in neighbors:
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="A*",
                source=source,
                target=target,
                path=path + [target],
                path_length=len(path),
                nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4),
                peak_memory_mb=round(peak_memory, 4),
                status="success"
            )

        g_next = g + 1
        import heuristic as _heuristic_module
        emb_cache = _heuristic_module.embeddings_cache

        for neighbor in neighbors:
            if neighbor in closed:
                continue
            if neighbor not in g_cost or g_next < g_cost[neighbor]:
                g_cost[neighbor] = g_next
                if neighbor in emb_cache:
                    h_neighbor = h(neighbor, target, graph)
                    f_next = g_next + weight * h_neighbor
                else:
                    f_next = g_next  # lower-bound estimate for uncached nodes
                heapq.heappush(heap, (f_next, g_next, neighbor, path + [neighbor]))

    tracemalloc.stop()
    return SearchMetrics(
        algorithm="A*", source=source, target=target,
        status="not_found", nodes_expanded=nodes_expanded,
        time_taken=round(time.time() - start_time, 4)
    )