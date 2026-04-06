import feedparser
from typing import Generator
from .models import ArticleResult

RSS_URL = "https://www.barandbench.com/feed"

def fetch_feed_items(seen_urls: set) -> Generator[dict, None, None]:
    """
    Fetches RSS, yields only unseen items as dicts.
    Caller is responsible for updating seen_urls after processing.
    """
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        url = entry.get("link", "").strip()
        if not url or url in seen_urls:
            continue
        # feedparser puts <category> tags into entry.tags as list of dicts
        # each dict has keys: 'term', 'scheme', 'label'
        tags = entry.get("tags", [])
        # last tag is usually the most specific — e.g. "Litigation News" not just "News"
        category = tags[-1]["term"] if tags else None

        yield {
            "url": url,
            "title": entry.get("title", ""),
            "published": entry.get("published", None),
            "author": entry.get("author", None),
            "category": category,
        }