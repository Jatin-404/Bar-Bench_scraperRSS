from scraper.models import ArticleResult

# In-memory store — swap for Redis/DB later
seen_urls: set[str] = set()
articles: list[ArticleResult] = []   # newest first


#Why a separate state.py? FastAPI runs in a single process — you can't share state via globals in main.py without circular imports. This module is imported by both the scheduler and the routes.