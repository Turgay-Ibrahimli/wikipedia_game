# Heuristic function — loads sentence-transformers model, computes embeddings, cosine similarity, caching
# heuristic.py
import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDINGS_CACHE = "cache/embeddings_cache.pkl"

def _load_embeddings_cache():
    if not os.path.exists(EMBEDDINGS_CACHE):
        return {}
    with open(EMBEDDINGS_CACHE, "rb") as f:
        content = f.read()
        if not content:  # handle empty file
            return {}
        return pickle.loads(content)

def _save_embeddings_cache(cache):
    os.makedirs("cache", exist_ok=True)
    with open(EMBEDDINGS_CACHE, "wb") as f:
        pickle.dump(cache, f)

embeddings_cache = _load_embeddings_cache()

def get_embedding(page_title, wiki_graph):
    if page_title in embeddings_cache:
        return embeddings_cache[page_title]
    
    summary = wiki_graph.get_summary(page_title)
    if not summary:
        summary = page_title  # fallback if no summary
    
    embedding = model.encode(summary, convert_to_numpy=True)
    embeddings_cache[page_title] = embedding
    _save_embeddings_cache(embeddings_cache)
    return embedding

def h(page, target, wiki_graph):
    """
    Heuristic function for informed search.
    Returns 1 - cosine_similarity between the embeddings of page and target summaries.
    Score of 0 means semantically identical, 1 means completely unrelated.
    """
    emb_page = get_embedding(page, wiki_graph)
    emb_target = get_embedding(target, wiki_graph)
    
    cosine_sim = np.dot(emb_page, emb_target) / (
        np.linalg.norm(emb_page) * np.linalg.norm(emb_target)
    )
    return 1 - float(cosine_sim)