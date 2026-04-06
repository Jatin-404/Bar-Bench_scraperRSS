from fastapi import APIRouter, HTTPException, Query
from scraper.models import ArticleResult
import state
import scheduler

router = APIRouter(prefix="/api/v1", tags=["scraper"])


@router.get("/articles", response_model=list[ArticleResult])
async def get_articles(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated list of scraped articles, newest first."""
    return state.articles[offset : offset + limit]


@router.get("/articles/count")
async def get_count():
    return {"total": len(state.articles)}


@router.post("/scrape", response_model=ArticleResult)
async def scrape_now(url: str):
    # Auto-add scheme if missing
    if not url.startswith("http"):
        url = "https://" + url

    if "barandbench.com" not in url:
        raise HTTPException(status_code=400, detail="Only barandbench.com URLs allowed")

    import asyncio
    from scraper.article import scrape_article as _scrape

    try:
        loop = asyncio.get_event_loop()
        scraped = await loop.run_in_executor(None, _scrape, url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scrape failed: {e}")

    return ArticleResult(
        url=url,
        title="(manual scrape)",
        published=None,
        author=None,
        category=scraped["category"],
        full_text=scraped["full_text"],
    )


@router.post("/poll", status_code=202)
async def trigger_poll():
    """Manually trigger an RSS poll right now (don't wait 5 min)."""
    import asyncio
    asyncio.create_task(scheduler._run_once())
    return {"message": "Poll triggered"}