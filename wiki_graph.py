 # WikiGraph class — fetches pages, returns neighbors (handles API calls, link parsing, caching)

import wikipediaapi
import json
import os

class WikiGraph:
    def __init__(self, cache_path="cache/links_cache.json"):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent="WikipediaGame/1.0 (your_email@example.com)",
            language="en"
        )
        self.cache_path = cache_path
        self.cache = self._load_cache()

        # Prefixes to filter out — these aren't real articles
        self.skip_prefixes = (
            "Category:", "Help:", "File:", "Template:",
            "Wikipedia:", "Special:", "Talk:", "Portal:",
            "Draft:", "Module:", "MediaWiki:", "User:"
        )

    def _load_cache(self):
        if not os.path.exists(self.cache_path):  # cache_file -> cache_path
            return {}
        
        with open(self.cache_path, 'r') as f:    # cache_file -> cache_path
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)

    def save_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def get_neighbors(self, page_title):
        """Return list of outgoing link titles from a Wikipedia page."""
        if page_title in self.cache:
            return self.cache[page_title]

        page = self.wiki.page(page_title)
        if not page.exists():
            self.cache[page_title] = []
            return []

        links = [
            title for title in page.links.keys()
            if not title.startswith(self.skip_prefixes)
        ]

        self.cache[page_title] = links
        return links

    def get_summary(self, page_title):
        """Return the summary (first paragraph) of a page — used by heuristic later."""
        page = self.wiki.page(page_title)
        if not page.exists():
            return ""
        return page.summary

    def page_exists(self, page_title):
        return self.wiki.page(page_title).exists()