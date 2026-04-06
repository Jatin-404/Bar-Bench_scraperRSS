import asyncio
from scraper.feed import fetch_feed_items
from scraper.article import scrape_article
from scraper.models import ArticleResult
import state

POLL_INTERVAL = 300  # seconds

async def poll_loop():
    """Runs forever in the background. Called once on app startup."""
    while True:
        print("[scheduler] Polling RSS...")
        await _run_once()
        print(f"[scheduler] Sleeping {POLL_INTERVAL}s")
        await asyncio.sleep(POLL_INTERVAL)


async def _run_once():
    loop = asyncio.get_event_loop()

    # feedparser is sync — run in thread pool so we don't block the event loop
    items = await loop.run_in_executor(
        None, _fetch_new_items
    )

    for item in items:
        url = item["url"]
        try:
            # httpx sync call — also offloaded to thread pool
            scraped = await loop.run_in_executor(None, scrape_article, url)

            article = ArticleResult(
                url=url,
                title=item["title"],
                published=item["published"],
                author=item["author"],
                category=scraped["category"],
                full_text=scraped["full_text"],
            )

            state.seen_urls.add(url)
            state.articles.insert(0, article)  # newest first
            print(f"  ✓ {url} — {article.char_count} chars")

        except Exception as e:
            print(f"  ✗ {url} — {e}")


def _fetch_new_items() -> list[dict]:
    return list(fetch_feed_items(state.seen_urls))