# search/greedy.py
import time
import tracemalloc
import heapq
from metrics import SearchMetrics
from heuristic import h, cosine_distances_to_target

def greedy(source, target, graph, max_nodes=10000, *, timeout_seconds: float | None = None, log_every: int | None = None):
    """
    Greedy Best-First Search over the Wikipedia link graph.
    
    Uses a priority queue ordered by h(n) — the semantic similarity between
    the current page and the target. Always expands the node that looks most
    promising according to the heuristic, without considering the cost to get there.
    This makes it fast but not guaranteed to find the shortest path — it can get
    misled by the heuristic and find a suboptimal route.
    """
    start_time = time.time()
    deadline = (time.perf_counter() + float(timeout_seconds)) if timeout_seconds is not None else None
    tracemalloc.start()

    visited = set()
    # heap entries: (h_score, path)
    heap = [(h(source, target, graph), [source])]
    nodes_expanded = 0
    last_path = [source]

    while heap:
        if deadline is not None and time.perf_counter() >= deadline:
            tracemalloc.stop()
            return SearchMetrics(
                algorithm="Greedy",
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
                algorithm="Greedy", source=source, target=target,
                status="timeout", nodes_expanded=nodes_expanded,
                time_taken=round(time.time() - start_time, 4)
            )

        score, path = heapq.heappop(heap)
        current = path[-1]
        last_path = path

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1

        if log_every and nodes_expanded % log_every == 0:
            print(f"[Greedy] expanded={nodes_expanded} current={current!r} h={score:.4f} heap={len(heap)} visited={len(visited)}")

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

        candidates = [n for n in neighbors if n not in visited]
        scores = cosine_distances_to_target(candidates, target, graph)
        for neighbor, score in zip(candidates, scores, strict=False):
            heapq.heappush(heap, (score, path + [neighbor]))

    tracemalloc.stop()
    return SearchMetrics(
        algorithm="Greedy", source=source, target=target,
        status="not_found", nodes_expanded=nodes_expanded,
        time_taken=round(time.time() - start_time, 4)
    )
