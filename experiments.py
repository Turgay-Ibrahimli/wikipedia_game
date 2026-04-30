from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Process, Queue
from queue import Empty
from typing import Any

from metrics import SearchMetrics


EXPERIMENT_MAX_NODES = 10_000
EXPERIMENT_TIMEOUT_SECONDS = 300
EXPERIMENT_DFS_MAX_DEPTH = 6
EXPERIMENT_ALGORITHMS = ("bfs", "dfs", "greedy", "astar")

EXPERIMENT_TIERS = {
    "easy": [
        ("Python (programming language)", "Guido van Rossum"),
        ("Physics", "Quantum mechanics"),
        ("Computer science", "Algorithm"),
    ],
    "medium": [
        ("Python (programming language)", "Alan Turing"),
        ("Machine learning", "Statistics"),
        ("World War II", "Winston Churchill"),
    ],
    "hard": [
        ("Python (programming language)", "Napoleon"),
        ("Basketball", "Philosophy"),
        ("Solar System", "French Revolution"),
    ],
}


@dataclass(frozen=True)
class ExperimentCase:
    tier: str
    source: str
    target: str


def get_experiment_cases() -> list[ExperimentCase]:
    cases: list[ExperimentCase] = []
    for tier, pairs in EXPERIMENT_TIERS.items():
        for source, target in pairs:
            cases.append(ExperimentCase(tier=tier, source=source, target=target))
    return cases


def get_experiment_pairs() -> list[tuple[str, str]]:
    return [(case.source, case.target) for case in get_experiment_cases()]


def get_experiment_tiers() -> dict[str, list[tuple[str, str]]]:
    return {tier: list(pairs) for tier, pairs in EXPERIMENT_TIERS.items()}


def _algorithm_label(name: str) -> str:
    labels = {
        "bfs": "BFS",
        "dfs": "DFS",
        "greedy": "Greedy",
        "astar": "A*",
    }
    return labels[name.lower()]


def _load_runner(name: str) -> Any:
    name = name.lower()
    if name == "bfs":
        from search.bfs import bfs

        return bfs
    if name == "dfs":
        from search.dfs import dfs

        return dfs
    if name == "greedy":
        from search.greedy import greedy

        return greedy
    if name == "astar":
        from search.astar import astar

        return astar
    raise ValueError(f"Unknown algorithm: {name!r}")


def _run_algorithm(
    algorithm: str,
    source: str,
    target: str,
    max_nodes: int,
    max_depth: int,
    weight: float,
) -> SearchMetrics:
    from wiki_graph import WikiGraph

    graph = WikiGraph()
    runner = _load_runner(algorithm)
    try:
        if algorithm.lower() == "dfs":
            return runner(source, target, graph, max_depth=max_depth, max_nodes=max_nodes)
        if algorithm.lower() == "astar":
            return runner(source, target, graph, max_nodes=max_nodes, weight=weight)
        return runner(source, target, graph, max_nodes=max_nodes)
    finally:
        graph.save_cache()


def _worker(
    queue: Queue,
    algorithm: str,
    source: str,
    target: str,
    max_nodes: int,
    max_depth: int,
    weight: float,
) -> None:
    try:
        result = _run_algorithm(
            algorithm=algorithm,
            source=source,
            target=target,
            max_nodes=max_nodes,
            max_depth=max_depth,
            weight=weight,
        )
    except Exception as exc:
        result = SearchMetrics(
            algorithm=_algorithm_label(algorithm),
            source=source,
            target=target,
            status=f"error: {exc}",
        )
    queue.put(result)


def run_with_timeout(
    algorithm: str,
    source: str,
    target: str,
    *,
    max_nodes: int = EXPERIMENT_MAX_NODES,
    timeout_seconds: int = EXPERIMENT_TIMEOUT_SECONDS,
    max_depth: int = EXPERIMENT_DFS_MAX_DEPTH,
    weight: float = 3.0,
) -> SearchMetrics:
    queue: Queue = Queue()
    process = Process(
        target=_worker,
        args=(queue, algorithm, source, target, max_nodes, max_depth, weight),
    )
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return SearchMetrics(
            algorithm=_algorithm_label(algorithm),
            source=source,
            target=target,
            status="timeout",
            time_taken=float(timeout_seconds),
        )

    try:
        return queue.get_nowait()
    except Empty:
        return SearchMetrics(
            algorithm=_algorithm_label(algorithm),
            source=source,
            target=target,
            status="error: no result returned",
        )


if __name__ == "__main__":
    from main import main

    raise SystemExit(main(["--experiments", "--all-algorithms"]))
