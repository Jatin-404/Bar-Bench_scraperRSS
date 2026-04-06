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
        yield {
            "url": url,
            "title": entry.get("title", ""),
            "published": entry.get("published", None),
            "author": entry.get("author", None),
        }