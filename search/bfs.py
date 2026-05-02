# search/bfs.py
import time
import tracemalloc
from collections import deque
from metrics import SearchMetrics

def bfs(source, target, graph, max_nodes=10000, *, timeout_seconds: float | None = None, log_every: int | None = None):
    """
    BFS over the Wikipedia link graph.
    
    Key design decision: we check if the target appears in a page's neighbor list
    BEFORE adding neighbors to the queue, not after popping them. This avoids
    making unnecessary API calls for nodes that come alphabetically after the target,
    which would otherwise cause massive slowdowns even for 1-hop paths.
    """
    start_time = time.time()
    deadline = (time.perf_counter() + float(timeout_seconds)) if timeout_seconds is not None else None
    tracemalloc.start()
    visited = {source}
    queue = deque([[source]])
    nodes_expanded = 0
    last_path = [source]

    while queue:
        if deadline is not None and time.perf_counter() >= deadline:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="BFS",
                source=source,
                target=target,
                path=last_path,
                path_length=max(0, len(last_path) - 1),
                status="timeout",
                nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4),
            )
        if nodes_expanded >= max_nodes:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="BFS", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        path = queue.popleft()
        current = path[-1]
        last_path = path
        nodes_expanded += 1

        if log_every and nodes_expanded % log_every == 0:
            print(f"[BFS] expanded={nodes_expanded} current={current!r} queue={len(queue)} visited={len(visited)}")

        neighbors = graph.get_neighbors(current)

        # ✅ Check target immediately before queuing anything
        if target in neighbors:
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="BFS",
                source=source,
                target=target,
                path=path + [target],
                path_length=len(path),
                nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4),
                peak_memory_mb=round(peak_memory, 4),
                status="success"
            )

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    tracemalloc.stop()
    return SearchMetrics(
        algorithm="BFS", source=source, target=target,
        status="not_found", nodes_expanded=nodes_expanded,
        time_taken=round(time.time() - start_time, 4)
    )
