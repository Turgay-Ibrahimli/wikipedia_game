from __future__ import annotations

import os
import pickle
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDINGS_CACHE = "cache/embeddings_cache.pkl"


def _load_embeddings_cache() -> dict[str, np.ndarray]:
    if not os.path.exists(EMBEDDINGS_CACHE):
        return {}
    with open(EMBEDDINGS_CACHE, "rb") as f:
        content = f.read()
        if not content:
            return {}
        return pickle.loads(content)


def _save_embeddings_cache(cache: dict[str, np.ndarray]) -> None:
    os.makedirs("cache", exist_ok=True)
    with open(EMBEDDINGS_CACHE, "wb") as f:
        pickle.dump(cache, f)


embeddings_cache: dict[str, np.ndarray] = _load_embeddings_cache()


def get_embedding(page_title: str, wiki_graph=None) -> np.ndarray:
    """
    Return an embedding for `page_title`.

    We embed the title string directly (no Wikipedia summary fetch). This avoids
    hundreds of network calls per neighbor expansion.

    `wiki_graph` is accepted for backwards compatibility but is unused.
    """
    if page_title in embeddings_cache:
        return embeddings_cache[page_title]

    embedding = model.encode(page_title, convert_to_numpy=True)
    embeddings_cache[page_title] = embedding
    _save_embeddings_cache(embeddings_cache)
    return embedding


def get_embeddings_batch(page_titles: Iterable[str]) -> dict[str, np.ndarray]:
    """
    Ensure embeddings exist for all `page_titles`, encoding missing ones in a
    single batch call. Returns a mapping for the requested titles.
    """
    titles = list(page_titles)
    missing = [t for t in titles if t not in embeddings_cache]
    if missing:
        batch = model.encode(missing, convert_to_numpy=True)
        for title, emb in zip(missing, batch, strict=False):
            embeddings_cache[title] = emb
        _save_embeddings_cache(embeddings_cache)

    return {t: embeddings_cache[t] for t in titles}


def cosine_distances_to_target(pages: list[str], target: str, wiki_graph=None) -> list[float]:
    """
    Vectorized distances for a list of pages to a single target.
    Returns: list of 1 - cosine_similarity, aligned with `pages`.
    """
    if not pages:
        return []

    emb_target = get_embedding(target, wiki_graph)
    mapping = get_embeddings_batch(pages)
    matrix = np.stack([mapping[p] for p in pages], axis=0)

    target_norm = float(np.linalg.norm(emb_target))
    if target_norm == 0.0:
        return [1.0 for _ in pages]

    row_norms = np.linalg.norm(matrix, axis=1)
    denom = row_norms * target_norm
    denom = np.where(denom == 0.0, 1.0, denom)
    cosine_sims = (matrix @ emb_target) / denom
    return (1.0 - cosine_sims).astype(float).tolist()


def h(page: str, target: str, wiki_graph=None) -> float:
    """
    Heuristic function for informed search.
    Returns 1 - cosine_similarity between the embeddings of page and target.
    Score of 0 means semantically identical, 1 means completely unrelated.
    """
    emb_page = get_embedding(page, wiki_graph)
    emb_target = get_embedding(target, wiki_graph)

    denom = float(np.linalg.norm(emb_page) * np.linalg.norm(emb_target))
    if denom == 0.0:
        return 1.0
    cosine_sim = float(np.dot(emb_page, emb_target) / denom)
    return 1.0 - cosine_sim
