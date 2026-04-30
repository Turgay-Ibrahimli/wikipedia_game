"""
CLI entry point for running searches on the Wikipedia link graph.

Run from repo root:
  python wikipedia_game/main.py --source "Python (programming language)" --target "Napoleon" --algorithm greedy

Or run a set of pairs:
  python wikipedia_game/main.py --algorithm bfs --pair "Python (programming language)" "Computer science" --pair "Python (programming language)" "Napoleon"
"""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Callable, Iterable, Any

if TYPE_CHECKING:
    from metrics import SearchMetrics
    from wiki_graph import WikiGraph


def _load_runner(algorithm: str) -> Callable[..., Any]:
    # Import lazily so BFS/DFS runs don't pay the cost of loading the embedding model.
    algorithm = algorithm.lower()
    if algorithm == "bfs":
        from search.bfs import bfs

        return bfs
    if algorithm == "dfs":
        from search.dfs import dfs

        return dfs
    if algorithm == "greedy":
        from search.greedy import greedy

        return greedy
    if algorithm == "astar":
        from search.astar import astar

        return astar
    raise SystemExit(f"Unknown algorithm: {algorithm!r} (expected bfs/dfs/greedy/astar)")


def _print_result(result: Any) -> None:
    header = f"{result.algorithm} | {result.source} -> {result.target}"
    print("=" * len(header))
    print(header)
    print("=" * len(header))
    print(
        f"status={result.status} | expanded={result.nodes_expanded} | time={result.time_taken}s | peak_mem={result.peak_memory_mb}MB"
    )
    if result.path:
        print("path:", " -> ".join(result.path))
        print("hops:", result.path_length)


def _run_pairs(
    graph: Any,
    pairs: Iterable[tuple[str, str]],
    algorithm: str,
    *,
    max_nodes: int,
    max_depth: int,
    weight: float,
    timeout_seconds: int | None = None,
) -> list[Any]:
    results: list[SearchMetrics] = []
    use_timeout = timeout_seconds is not None

    if use_timeout:
        from experiments import run_with_timeout
    else:
        runner = _load_runner(algorithm)

    for source, target in pairs:
        if use_timeout:
            result = run_with_timeout(
                algorithm,
                source,
                target,
                max_nodes=max_nodes,
                timeout_seconds=timeout_seconds,
                max_depth=max_depth,
                weight=weight,
            )
        else:
            if algorithm.lower() == "dfs":
                result = runner(source, target, graph, max_depth=max_depth, max_nodes=max_nodes)
            elif algorithm.lower() == "astar":
                result = runner(source, target, graph, max_nodes=max_nodes, weight=weight)
            else:
                result = runner(source, target, graph, max_nodes=max_nodes)

        results.append(result)
        _print_result(result)
        print()

    return results

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wikipedia Game search runner")

    parser.add_argument("--source", help="Source Wikipedia page title")
    parser.add_argument("--target", help="Target Wikipedia page title")
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        metavar=("SOURCE", "TARGET"),
        help="Run a specific (source, target) pair. Can be repeated.",
    )
    parser.add_argument(
        "--algorithm",
        default="greedy",
        choices=["bfs", "dfs", "greedy", "astar"],
        help="Search algorithm to run",
    )
    parser.add_argument(
        "--all-algorithms",
        action="store_true",
        help="Run bfs/dfs/greedy/astar for each pair (overrides --algorithm)",
    )
    parser.add_argument("--max-nodes", type=int, default=None, help="Stop after expanding this many nodes")
    parser.add_argument("--max-depth", type=int, default=6, help="DFS depth limit (only used for dfs)")
    parser.add_argument("--weight", type=float, default=3.0, help="A* heuristic weight (only used for astar)")
    parser.add_argument("--experiments", action="store_true", help="Run the built-in experiment pairs")
    parser.add_argument("--timeout-seconds", type=int, default=None, help="Wall-clock timeout per run")
    parser.add_argument("--csv", default="results/results.csv", help="If set, writes results to this CSV path")

    args = parser.parse_args(argv)

    from experiments import EXPERIMENT_DFS_MAX_DEPTH, EXPERIMENT_MAX_NODES, EXPERIMENT_TIMEOUT_SECONDS, get_experiment_pairs
    from metrics import export_to_csv
    from wiki_graph import WikiGraph

    max_nodes = args.max_nodes
    timeout_seconds = args.timeout_seconds
    max_depth = args.max_depth

    graph = WikiGraph()
    try:
        if args.experiments:
            pairs = get_experiment_pairs()
            if max_nodes is None:
                max_nodes = EXPERIMENT_MAX_NODES
            if timeout_seconds is None:
                timeout_seconds = EXPERIMENT_TIMEOUT_SECONDS
            if args.max_depth == 6:
                max_depth = EXPERIMENT_DFS_MAX_DEPTH
        elif args.pair:
            pairs = [(a, b) for a, b in args.pair]
        else:
            if not args.source or not args.target:
                raise SystemExit("Provide --source/--target, or use --pair, or pass --experiments.")
            pairs = [(args.source, args.target)]

        if max_nodes is None:
            max_nodes = 500

        algorithms = ["bfs", "dfs", "greedy", "astar"] if args.all_algorithms else [args.algorithm]
        results: list[Any] = []
        for algorithm in algorithms:
            results.extend(
                _run_pairs(
                    graph,
                    pairs,
                    algorithm,
                    max_nodes=max_nodes,
                    max_depth=max_depth,
                    weight=args.weight,
                    timeout_seconds=timeout_seconds,
                )
            )
        if args.csv:
            export_to_csv(results, filepath=args.csv)
    finally:
        graph.save_cache()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
