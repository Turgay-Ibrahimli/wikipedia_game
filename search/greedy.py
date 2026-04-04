# search/greedy.py
import time
import tracemalloc
import heapq
from metrics import SearchMetrics
from heuristic import h

def greedy(source, target, graph, max_nodes=10000):
    """
    Greedy Best-First Search over the Wikipedia link graph.
    
    Uses a priority queue ordered by h(n) — the semantic similarity between
    the current page and the target. Always expands the node that looks most
    promising according to the heuristic, without considering the cost to get there.
    This makes it fast but not guaranteed to find the shortest path — it can get
    misled by the heuristic and find a suboptimal route.
    """
    start_time = time.time()
    tracemalloc.start()

    visited = set()
    # heap entries: (h_score, path)
    heap = [(h(source, target, graph), [source])]
    nodes_expanded = 0

    while heap:
        if nodes_expanded >= max_nodes:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="Greedy", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        _, path = heapq.heappop(heap)
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1

        neighbors = graph.get_neighbors(current)

        # Early target detection
        if target in neighbors:
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="Greedy",
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
                score = h(neighbor, target, graph)
                heapq.heappush(heap, (score, path + [neighbor]))

    tracemalloc.stop()
    return SearchMetrics(
        algorithm="Greedy", source=source, target=target,
        status="not_found", nodes_expanded=nodes_expanded,
        time_taken=round(time.time() - start_time, 4)
    )