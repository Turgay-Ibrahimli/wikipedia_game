import os
import sys

from flask import render_template
from flask import Flask, request, jsonify
from flask_cors import CORS

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from search.astar import astar
from search.bfs import bfs
from search.dfs import dfs
from search.greedy import greedy
from wiki_graph import WikiGraph

app = Flask(__name__)
CORS(app)

graph = WikiGraph()

ALGORITHM_MAP = {
    "bfs": bfs,
    "dfs": dfs,
    "greedy": greedy,
    "astar": astar,
}

@app.route('/')
def home():
    return render_template("index.html")

def search_metrics_to_dict(metrics):
    return {
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

@app.route('/search', methods=['POST'])
def search():
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
        algorithm_fn = load_runner(algorithm_key)
    except Exception as e:
        import traceback
        traceback.print_exc()   # 🔥 THIS is key
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

    try:
        # handle different signatures
        if algorithm_key == "dfs":
            metrics = algorithm_fn(source, target, graph, max_depth=6, max_nodes=500)
        elif algorithm_key == "astar":
            metrics = algorithm_fn(source, target, graph, max_nodes=500, weight=3.0)
        else:
            metrics = algorithm_fn(source, target, graph, max_nodes=500)

        return jsonify(search_metrics_to_dict(metrics))

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)