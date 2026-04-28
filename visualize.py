"""
Generate simple charts from `results/results.csv`.

Usage:
  python wikipedia_game/visualize.py
"""

from __future__ import annotations

import csv
import os
from collections import defaultdict


def _read_results(csv_path: str) -> list[dict[str, str]]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> int:
    csv_path = os.path.join("results", "results.csv")
    if not os.path.exists(csv_path):
        raise SystemExit(f"Missing {csv_path!r}. Run `python wikipedia_game/main.py ... --csv results/results.csv` first.")

    rows = _read_results(csv_path)

    # Group by algorithm label stored in the CSV (e.g. "BFS", "Greedy", "A*").
    nodes_by_algo: dict[str, list[float]] = defaultdict(list)
    time_by_algo: dict[str, list[float]] = defaultdict(list)
    hops_by_algo: dict[str, list[float]] = defaultdict(list)

    for row in rows:
        algo = row.get("algorithm") or "unknown"
        try:
            nodes_by_algo[algo].append(float(row.get("nodes_expanded") or 0))
            time_by_algo[algo].append(float(row.get("time_taken") or 0))
            hops_by_algo[algo].append(float(row.get("path_length") or 0))
        except ValueError:
            # Skip malformed rows.
            continue

    algos = sorted(nodes_by_algo.keys())
    nodes_means = [_mean(nodes_by_algo[a]) for a in algos]
    time_means = [_mean(time_by_algo[a]) for a in algos]
    hops_means = [_mean(hops_by_algo[a]) for a in algos]

    import matplotlib.pyplot as plt

    os.makedirs("results", exist_ok=True)

    def plot_bar(values: list[float], title: str, ylabel: str, out_name: str) -> None:
        plt.figure(figsize=(8, 4.5))
        plt.bar(algos, values)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(os.path.join("results", out_name), dpi=200)
        plt.close()

    plot_bar(time_means, "Mean Time Taken by Algorithm", "seconds", "time_by_algorithm.png")
    plot_bar(nodes_means, "Mean Nodes Expanded by Algorithm", "nodes", "nodes_by_algorithm.png")
    plot_bar(hops_means, "Mean Path Length by Algorithm", "hops", "hops_by_algorithm.png")

    print("Wrote:")
    print("  results/time_by_algorithm.png")
    print("  results/nodes_by_algorithm.png")
    print("  results/hops_by_algorithm.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
