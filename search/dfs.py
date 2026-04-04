# search/dfs.py
import time
import tracemalloc
from metrics import SearchMetrics

def dfs(source, target, graph, max_depth=6, max_nodes=10000):
    """
    Iterative DFS over the Wikipedia link graph with a depth limit.
    
    A depth limit is essential here — without it, DFS will follow chains
    of links indefinitely and never terminate. We use iterative DFS (explicit
    stack) rather than recursive to avoid Python's recursion limit.
    Like BFS, we check if the target appears in a page's neighbor list
    immediately after fetching, before pushing to the stack, to avoid
    unnecessary API calls.
    """
    start_time = time.time()
    tracemalloc.start()

    # Stack stores (path, depth)
    stack = [([source], 0)]
    visited = set()
    nodes_expanded = 0

    while stack:
        if nodes_expanded >= max_nodes:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="DFS", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        path, depth = stack.pop()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1

        if depth >= max_depth:
            continue

        neighbors = graph.get_neighbors(current)

        # Early target detection — same reasoning as BFS
        if target in neighbors:
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="DFS",
                source=source,
                target=target,
                path=path + [target],
                path_length=len(path),
                nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4),
                peak_memory_mb=round(peak_memory, 4),
                status="success"
            )

        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                stack.append((path + [neighbor], depth + 1))

    tracemalloc.stop()
    return SearchMetrics(
        algorithm="DFS", source=source, target=target,
        status="not_found", nodes_expanded=nodes_expanded,
        time_taken=round(time.time() - start_time, 4)
    )