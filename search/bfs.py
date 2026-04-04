# search/bfs.py
import time
import tracemalloc
from collections import deque
from metrics import SearchMetrics

def bfs(source, target, graph, max_nodes=10000):
    """
    BFS over the Wikipedia link graph.
    
    Key design decision: we check if the target appears in a page's neighbor list
    BEFORE adding neighbors to the queue, not after popping them. This avoids
    making unnecessary API calls for nodes that come alphabetically after the target,
    which would otherwise cause massive slowdowns even for 1-hop paths.
    """
    start_time = time.time()
    tracemalloc.start()
    visited = {source}
    queue = deque([[source]])
    nodes_expanded = 0

    while queue:
        if nodes_expanded >= max_nodes:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="BFS", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        path = queue.popleft()
        current = path[-1]
        nodes_expanded += 1

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