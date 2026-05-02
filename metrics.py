# Tracks path length, nodes expanded, time, memory per run; utility class or dataclass

# metrics.py
import csv
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchMetrics:
    algorithm: str
    source: str
    target: str
    path: Optional[list] = None
    path_length: int = 0
    nodes_expanded: int = 0
    time_taken: float = 0.0
    peak_memory_mb: float = 0.0
    status: str = "success"  # or "timeout" / "not_found"

def export_to_csv(metrics_list: list[SearchMetrics], filepath="results/results.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "source", "target", "path_length",
                         "nodes_expanded", "time_taken", "peak_memory_mb", "status", "path"])
        for m in metrics_list:
            writer.writerow([
                m.algorithm, m.source, m.target, m.path_length,
                m.nodes_expanded, m.time_taken, m.peak_memory_mb,
                m.status, " -> ".join(m.path) if m.path else ""
            ])
