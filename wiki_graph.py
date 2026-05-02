# WikiGraph class - fetches Wikipedia pages and exposes a neighbor/summary API.

from __future__ import annotations

import json
import os
import random
import time
from typing import Callable, TypeVar

import wikipediaapi

_T = TypeVar("_T")


class WikiGraph:
    def __init__(self, cache_path: str = "cache/links_cache.json"):
        # Wikipedia expects a descriptive UA with contact info. The placeholder UA can
        # trigger throttling or dropped connections.
        user_agent = os.getenv(
            "WIKIPEDIA_USER_AGENT",
            "WikipediaGame/1.0 (contact: set WIKIPEDIA_USER_AGENT)",
        )
        timeout_s = float(os.getenv("WIKIPEDIA_TIMEOUT", "10.0"))

        # wikipedia-api forwards kwargs (like timeout) into request kwargs.
        self.wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language="en", timeout=timeout_s)
        self.cache_path = cache_path
        self.cache = self._load_cache()

        self._warned_network_error = False

        # Prefixes to filter out - these aren't real articles.
        self.skip_prefixes = (
            "Category:",
            "Help:",
            "File:",
            "Template:",
            "Wikipedia:",
            "Special:",
            "Talk:",
            "Portal:",
            "Draft:",
            "Module:",
            "MediaWiki:",
            "User:",
        )

    def _with_retries(self, fn: Callable[[], _T], *, attempts: int = 3, base_delay_s: float = 0.4) -> _T:
        last_exc: Exception | None = None
        for i in range(attempts):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                # Exponential backoff with small jitter to avoid hammering Wikipedia.
                delay = base_delay_s * (2**i) + random.random() * 0.2
                time.sleep(delay)

        assert last_exc is not None
        raise last_exc

    def _maybe_warn_network(self, err: Exception) -> None:
        if self._warned_network_error:
            return
        self._warned_network_error = True
        print(
            "Warning: Wikipedia request failed (network/rate-limit). "
            "Set WIKIPEDIA_USER_AGENT to a real contact string and retry."
        )
        print(f"  details: {type(err).__name__}: {err}")

    def _load_cache(self) -> dict:
        if not os.path.exists(self.cache_path):
            return {}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            # Cache can be corrupted if the process is interrupted mid-write.
            try:
                corrupt_path = f"{self.cache_path}.corrupt-{time.strftime('%Y%m%d-%H%M%S')}"
                os.replace(self.cache_path, corrupt_path)
                print(f"Warning: links cache was corrupted; moved to {corrupt_path}.")
            except Exception:
                print("Warning: links cache was corrupted; ignoring and rebuilding.")
            print(f"  details: {type(exc).__name__}: {exc}")
            return {}

    def save_cache(self) -> None:
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        tmp_path = f"{self.cache_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f)
        os.replace(tmp_path, self.cache_path)

    def get_neighbors(self, page_title: str) -> list[str]:
        """Return list of outgoing link titles from a Wikipedia page."""
        if page_title in self.cache:
            return self.cache[page_title]

        try:
            page = self.wiki.page(page_title)

            def _fetch_links() -> list[str]:
                if not page.exists():
                    return []
                return [
                    title
                    for title in page.links.keys()
                    if not title.startswith(self.skip_prefixes)
                ]

            links = self._with_retries(_fetch_links)
        except Exception as exc:
            self._maybe_warn_network(exc)
            # Don't cache failures; they might succeed later.
            return []

        self.cache[page_title] = links
        return links

    def get_summary(self, page_title: str) -> str:
        """Return the summary of a page - used by the embedding heuristic."""
        try:
            page = self.wiki.page(page_title)

            def _fetch_summary() -> str:
                if not page.exists():
                    return ""
                return page.summary or ""

            return self._with_retries(_fetch_summary)
        except Exception as exc:
            self._maybe_warn_network(exc)
            return ""

    def page_exists(self, page_title: str) -> bool:
        try:
            return self.wiki.page(page_title).exists()
        except Exception as exc:
            self._maybe_warn_network(exc)
            return False
