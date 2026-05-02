from __future__ import annotations

import os
import sys
from multiprocessing import Process, Queue
from queue import Empty
from threading import Lock
import time

from flask import render_template
from flask import Flask, request, jsonify
from flask_cors import CORS

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from wiki_graph import WikiGraph

app = Flask(__name__)
CORS(app)

_active_lock = Lock()
_active_process: Process | None = None
_active_queue: Queue | None = None

@app.route('/')
def home():
    return render_template("index.html")

def search_metrics_to_dict(metrics):
    payload = {
        "algorithm": metrics.algorithm,
        "source": metrics.source,
        "target": metrics.target,
        "path": metrics.path or [],
        "path_length": metrics.path_length,
        "nodes_expanded": metrics.nodes_expanded,
        "time_taken": metrics.time_taken,
        "peak_memory_mb": metrics.peak_memory_mb,
        "status": metrics.status,
    }
    return payload

def load_runner(algorithm: str):
    algorithm = algorithm.lower()

    if algorithm == "bfs":
        from search.bfs import bfs
        return bfs
    elif algorithm == "dfs":
        from search.dfs import dfs
        return dfs
    elif algorithm == "greedy":
        from search.greedy import greedy
        return greedy
    elif algorithm == "astar":
        from search.astar import astar
        return astar

    raise ValueError(f"Unknown algorithm: {algorithm}")

def _terminate_active_search_locked() -> None:
    global _active_process, _active_queue

    if _active_process is None:
        return

    try:
        if _active_process.is_alive():
            _active_process.terminate()
            _active_process.join(timeout=1.0)
    finally:
        _active_process = None
        _active_queue = None

def _search_worker(
    queue: Queue,
    *,
    algorithm_key: str,
    source: str,
    target: str,
    max_nodes: int,
    max_depth: int,
    weight: float,
    timeout_seconds: float,
    log_every: int | None,
) -> None:
    t0 = time.perf_counter()
    try:
        t_import_start = time.perf_counter()
        algorithm_fn = load_runner(algorithm_key)
        t_import_end = time.perf_counter()

        t_graph_start = time.perf_counter()
        graph = WikiGraph()
        t_graph_end = time.perf_counter()

        t_run_start = time.perf_counter()
        try:
            if algorithm_key == "dfs":
                metrics = algorithm_fn(
                    source,
                    target,
                    graph,
                    max_depth=max_depth,
                    max_nodes=max_nodes,
                    timeout_seconds=max(0.0, timeout_seconds - 0.5),
                    log_every=log_every,
                )
            elif algorithm_key == "astar":
                metrics = algorithm_fn(
                    source,
                    target,
                    graph,
                    max_nodes=max_nodes,
                    weight=weight,
                    timeout_seconds=max(0.0, timeout_seconds - 0.5),
                    log_every=log_every,
                )
            else:
                metrics = algorithm_fn(
                    source,
                    target,
                    graph,
                    max_nodes=max_nodes,
                    timeout_seconds=max(0.0, timeout_seconds - 0.5),
                    log_every=log_every,
                )
        finally:
            t_save_start = time.perf_counter()
            graph.save_cache()
            t_save_end = time.perf_counter()
        t_run_end = time.perf_counter()

        timings = {
            "worker_total_seconds": round(time.perf_counter() - t0, 6),
            "import_seconds": round(t_import_end - t_import_start, 6),
            "graph_init_seconds": round(t_graph_end - t_graph_start, 6),
            "algorithm_seconds_reported": metrics.time_taken,
            "algorithm_call_seconds": round(t_run_end - t_run_start, 6),
            "save_cache_seconds": round(t_save_end - t_save_start, 6),
        }

        queue.put({"ok": True, "metrics": search_metrics_to_dict(metrics), "timings": timings})
    except Exception as exc:
        queue.put({"ok": False, "error": str(exc)})

@app.route('/search', methods=['POST'])
def search():
    global _active_process, _active_queue

    data = request.json or {}
    print("Incoming request:", data)

    source = data.get('sourceValue', '').strip()
    target = data.get('targetValue', '').strip()
    algorithm_key = data.get('algorithm', '').strip().lower()

    if not source or not target:
        return jsonify({
            "error": "Both source and target page titles are required.",
            "status": "invalid_request"
        }), 400

    try:
        load_runner(algorithm_key)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 400

    max_nodes = int(data.get("maxNodes") or 500)
    max_depth = int(data.get("maxDepth") or 6)
    weight = float(data.get("weight") or 3.0)
    timeout_seconds = float(data.get("timeoutSeconds") or 300.0)
    log_every = int(data.get("logEvery") or 0) or None

    with _active_lock:
        # Single-flight: cancel any existing search, then start the new one.
        _terminate_active_search_locked()

        queue: Queue = Queue()
        proc = Process(
            target=_search_worker,
            kwargs={
                "queue": queue,
                "algorithm_key": algorithm_key,
                "source": source,
                "target": target,
                "max_nodes": max_nodes,
                "max_depth": max_depth,
                "weight": weight,
                "timeout_seconds": timeout_seconds,
                "log_every": log_every,
            },
        )
        _active_queue = queue
        _active_process = proc
        proc.start()

    proc.join(timeout_seconds)
    if proc.is_alive():
        with _active_lock:
            _terminate_active_search_locked()
        return jsonify({"status": "timeout", "error": "Search timed out."}), 504

    try:
        payload = queue.get_nowait()
    except Empty:
        # Most common cause: this request's worker was terminated by a newer
        # incoming request (single-flight cancellation).
        if proc.exitcode is not None and proc.exitcode != 0:
            return jsonify({"status": "canceled", "error": "Canceled by a newer search request."}), 409
        return jsonify({"status": "error", "error": "No result returned from search worker."}), 500

    if payload.get("ok"):
        response = payload["metrics"]
        response["timings"] = payload.get("timings") or {}
        return jsonify(response)
    return jsonify({"status": "error", "error": payload.get("error") or "Unknown error"}), 500

if __name__ == '__main__':
    # Threaded server allows a new request to arrive while another is running.
    # We disable the reloader to avoid multiple processes fighting over the
    # single-flight state and caches.
    app.run(debug=True, threaded=True, use_reloader=False)
