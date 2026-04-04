# test_graph.py (temporary, just to verify)
from wiki_graph import WikiGraph

graph = WikiGraph()

neighbors = graph.get_neighbors("Python (programming language)")
print(f"Found {len(neighbors)} links")
print(neighbors[:10])  # Print first 10

graph.save_cache()