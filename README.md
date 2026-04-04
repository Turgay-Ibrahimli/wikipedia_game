# Wikipedia Game — AI Search Project

This project explores the Wikipedia Game: given a source Wikipedia page and a target page, find a path between them using only hyperlinks. We model Wikipedia as a directed graph where pages are nodes and hyperlinks are edges, then compare how different search strategies perform on this navigation task.

We implemented four algorithms in order of increasing sophistication — BFS, DFS, Greedy Best-First Search, and A* — and built a semantic heuristic using sentence embeddings (all-MiniLM-L6-v2) and cosine similarity to guide the informed search algorithms. The core finding is that uninformed search (BFS, DFS) is practically infeasible beyond 1-2 hops due to Wikipedia's branching factor of ~700 links per page, while Greedy Best-First Search navigated from `Python (programming language)` to `Napoleon` in just 8 node expansions using the heuristic.

The project also includes a caching layer for both page links and embeddings, an experiment suite across easy/medium/hard page pairs, and result visualizations comparing all four algorithms on path length, nodes expanded, and time taken.

---

## Progress

- Step 1 ( Done ): Set up the project — create the folder structure, initialize a virtual environment, install dependencies (wikipedia-api, sentence-transformers, torch, numpy, matplotlib), and create requirements.txt.
- Step 2 ( Done ): Build wiki_graph.py — write a WikiGraph class with a get_neighbors(page_title) method that calls the Wikipedia API and returns a list of outgoing link titles from that page.
- Step 3 ( Done ): Add link filtering to wiki_graph.py — strip out non-article links (anything starting with "Category:", "Help:", "File:", "Template:", "Wikipedia:", "Special:", "Talk:", "Portal:") so only real article links remain.
- Step 4 ( Done ): Add caching to wiki_graph.py — before making an API call, check if the page's links are already in a local dictionary. Save the cache to cache/links_cache.json on disk so you don't repeat calls across runs.
- Step 5 ( Done ): Test the graph module — run get_neighbors on a few pages manually, print the results, and confirm you're getting clean article links back.
- Step 6 ( Done ): Create metrics.py — define a dataclass or dictionary structure to store: algorithm name, source, target, path found, path length, nodes expanded, time taken, and peak memory. Add a utility function to export results to CSV.
- Step 7 ( Done ): Implement BFS in search/bfs.py — standard queue-based BFS that takes source, target, and the graph object. Track visited nodes, reconstruct the path via parent pointers, and return the path plus metrics (nodes expanded, time).
- Step 8 ( Done ): Test BFS — run it on an easy pair like "Python (programming language)" → "Computer science". Verify the path makes sense and every link actually exists on the previous page.
- Step 9 ( Done ): Implement DFS in search/dfs.py — iterative DFS with a configurable depth limit (default around 6–8). Return the first path found plus metrics. Without a depth limit this will run forever, so the limit is essential.
- Step 10 ( Done ): Test DFS — run it on the same easy pair. Compare the path to BFS — it should be longer or equal, never shorter. Confirm the depth limit terminates properly.
- Step 11 ( Done ): Build heuristic.py — load a sentence-transformers model (all-MiniLM-L6-v2), write a function that takes a page title, fetches its summary (first paragraph) from Wikipedia, embeds it, and caches the embedding in cache/embeddings_cache.pkl.
- Step 12 ( Done ): Write the heuristic function — h(page, target) computes 1 - cosine_similarity(embedding(page), embedding(target)). Returns a float between 0 and 1 where 0 means semantically identical.
- Step 13 ( Done ): Test the heuristic — compute h for several pages against a fixed target. Check that semantically closer pages get lower scores (e.g., "Physics" should score lower than "Cooking" when the target is "Quantum mechanics").
- Step 14 ( Done ): Implement Greedy Best-First Search in search/greedy.py — use a priority queue ordered by h(n). Expand the node with the lowest heuristic value. Track metrics the same way as BFS/DFS.
- Step 15: Implement A* in search/astar.py — priority queue ordered by f(n) = g(n) + h(n) where g(n) is the number of hops so far. Use a closed set to avoid revisiting nodes. Track metrics.
- Step 16: Test both informed algorithms — run Greedy and A* on the same easy pair. Compare paths and nodes expanded against BFS. A* should find a path close to BFS-optimal; Greedy may find it faster but with a longer path.
- Step 17: Build experiments.py — define test pairs in three tiers: easy (3 pairs, closely related topics), medium (3 pairs, loosely related), hard (3 pairs, seemingly unrelated). Set a timeout of 5 minutes and a node expansion cap of 10,000 per run.
- Step 18: Run all experiments — loop over every test pair, run all four algorithms on each, collect metrics into a list, and save everything to results/results.csv. Handle timeouts gracefully by recording "timeout" instead of a path.
- Step 19: Build visualize.py — read results/results.csv and generate: a bar chart comparing nodes expanded across algorithms, a table of path lengths per pair, and a grouped chart showing time taken. Save plots to results/.
- Step 20: Write main.py and README.md — main.py should let you either run a single search (pick algorithm, source, target from command line) or trigger the full experiment suite. README.md documents the project overview, how to install, how to run, and a summary of your findings.

---

## BFS Performance Notes 4/4/2026, This was baseline BFS no embeddings so no heuristic assistance to the bfs, purely expanding nodes, which is impossible in the great scheme.

### Initial Run

Our first BFS test (`Python (programming language)` → `Guido van Rossum`) revealed a critical performance issue. Even though the target was just 1 hop away, BFS expanded **248 nodes** and took nearly **2 minutes**. The cause was that BFS was checking for the target only after popping nodes from the queue, meaning it made a live API call for every neighbor that came alphabetically before the target.

### What We Improved

We applied one targeted optimization: **early target detection**. Instead of checking for the target after popping from the queue, we now check if the target exists in a page's neighbor list immediately after fetching it, before queuing anything. This reduced the same 1-hop search from 248 nodes and 2 minutes down to **1 node expanded and ~0.0s**.

We also explored **parallel prefetching** using `ThreadPoolExecutor` — fetching an entire BFS frontier simultaneously rather than one page at a time. This was added to `wiki_graph.py` as `prefetch_neighbors()` and called from BFS before expanding each layer.

### Results After Optimization

| Path | Hops | Nodes Expanded | Time |
|------|------|----------------|------|
| Python → Guido van Rossum | 1 | 1 | ~0.0s |

### Fundamental Limitation

The early exit only helps the final layer. For multi-hop paths, every intermediate node still requires a live API call (~0.5s each). The branching factor of Wikipedia is roughly 700 links per page, meaning BFS is only realistically feasible for 1-2 hop paths. A 3-hop BFS would theoretically require fetching hundreds of thousands of pages.

### What We Did Not Try

- Pre-building and storing the full Wikipedia link graph locally (would require significant disk space and upfront crawl time)
- Wikipedia's bulk data dumps as an offline graph source
- Bidirectional BFS (searching from both source and target simultaneously), which would significantly reduce the search space

### Why We Stopped Here

Further optimizing BFS was not the primary goal of this project. The infeasibility of BFS beyond 2 hops is itself a meaningful result — it directly motivates the use of informed search algorithms (Greedy Best-First, A*) which avoid expanding the full frontier by using semantic similarity as a heuristic. BFS serves as our correctness baseline, not our performance target.

---

## DFS Performance Notes 4/4/2026, This was baseline DFS no embeddings so no heuristic assistance to the bfs, purely expanding nodes, which is impossible in the great scheme.

### Initial Run

We tested DFS on three pairs of increasing difficulty against the same source page (`Python (programming language)`). Results were:

| Target | Status | Nodes Expanded | Time |
|--------|--------|----------------|------|
| Guido van Rossum | success | 1 | 0.0s |
| Alan Turing | timeout | 500 | 3.5s |
| Napoleon | timeout | 500 | 0.0s |

### What We Implemented

We applied the same **early target detection** optimization from BFS — checking if the target exists in a page's neighbor list immediately after fetching, before pushing anything to the stack. We also used an **iterative stack** instead of recursion to avoid Python's recursion limit, and added a **depth limit** (default 6) which is essential for DFS on an effectively infinite graph like Wikipedia — without it, DFS would follow link chains indefinitely and never terminate.

### Interesting Observation

The Napoleon result is revealing — it hit 500 nodes in 0.0s because those pages were already in the cache from previous runs. This confirms that the real bottleneck is **API call latency**, not the algorithm itself. When the cache is warm, DFS burns through nodes extremely fast, which actually highlights how much the live fetching was masking the algorithm's true speed.

### Fundamental Limitation

DFS is poorly suited for this problem beyond 1-hop paths. Unlike BFS, DFS does not guarantee the shortest path — it follows one branch deeply before backtracking, which in a graph with ~700 links per page means it can go in completely the wrong direction for many hops before recovering. With a depth limit of 6 and a node cap of 500, it reliably finds direct neighbors but fails on anything requiring navigation across unrelated topics.

### What We Did Not Try

- Increasing the depth limit or node cap further (would just make timeouts slower, not fix the core problem)
- Bidirectional DFS
- Any form of ordering or prioritizing which neighbors to explore first — neighbors are currently explored in the order Wikipedia returns them, which is essentially alphabetical

### Why We Stopped Here

DFS, like BFS, serves as an uninformed baseline. Optimizing it further was not the goal — its failure on medium and hard pairs is the expected and useful result. It directly motivates the next phase: building a semantic heuristic using sentence embeddings, which will allow Greedy Best-First Search and A* to prioritize promising directions instead of exploring blindly.

---

## Greedy Best-First Search Performance Notes 4/4/2026, after adding heuristics and embeddings

### Initial Run

We tested Greedy Best-First Search on the same three pairs used for BFS and DFS. Results on the first (cold) run:

| Target | Status | Nodes Expanded | Path Length | Time |
|--------|--------|----------------|-------------|------|
| Guido van Rossum | success | 1 | 1 | 1.46s |
| Alan Turing | success | 2 | 2 | 418s |
| Napoleon | success | 8 | 4 | 445s |

### Second Run (Warm Cache)

| Target | Status | Nodes Expanded | Path Length | Time |
|--------|--------|----------------|-------------|------|
| Guido van Rossum | success | 1 | 1 | 0.0s |
| Alan Turing | success | 2 | 2 | 0.02s |
| Napoleon | success | 8 | 4 | 0.03s |

### What This Demonstrates

The cold vs warm run comparison confirms that the bottleneck is entirely API latency and embedding computation, not the algorithm itself. Once the cache is warm, Greedy solves all three pairs in under 0.03 seconds total. More importantly, Greedy found Napoleon in just 8 node expansions — DFS failed to find it within 500 nodes. This is the clearest evidence so far that the semantic heuristic is working as intended.

The path to Napoleon was:
`Python → Matrix multiplication → Jacques Philippe Marie Binet → King Louis-Philippe → Napoleon`

This is a genuinely interesting path — the heuristic navigated from a programming language through mathematics to French history in 4 hops.

### What We Did Not Try

- Tuning the heuristic (currently using raw cosine distance on full page summaries — chunking or weighting the summary differently might improve guidance)
- Handling heuristic ties — when multiple neighbors have very similar scores, the choice between them is essentially arbitrary
- Any form of beam search — limiting the number of neighbors pushed to the heap per expansion could significantly reduce memory usage
- Testing on pairs where the heuristic is likely to mislead (e.g. pages with ambiguous or very short summaries)

### Known Limitation

Greedy is not guaranteed to find the shortest path. It found a length-4 path to Napoleon, but a shorter path may exist — we have no way to verify this without running BFS to completion, which is infeasible. This is the core tradeoff Greedy makes: fewer expansions in exchange for optimality guarantees.

### Why We Stopped Here

Greedy is working well enough to serve its role in the project. The next step is A*, which adds path cost g(n) to the heuristic score, giving it the same guidance as Greedy but with a guarantee of finding the optimal path if the heuristic is admissible.
