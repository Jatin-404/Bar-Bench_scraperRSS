import httpx
from bs4 import BeautifulSoup
from typing import Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LegalNewsScraper/1.0)"
}

# Boilerplate lines to skip — exact strings that appear on every page
_SKIP_PHRASES = [
    "Follow Bar and Bench",
    "Download the Bar and Bench",
    "Loading content",
    "Bar and Bench Mobile app",
    "whatsapp.com/channel",
]

def scrape_article(url: str) -> dict:
    with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    return {
        "full_text": _extract_body(soup),
        "category": _extract_category(soup),
    }


def _extract_body(soup: BeautifulSoup) -> str:
    """
    Quintype CMS renders <p> tags directly in the page.
    Strategy: find the <h1>, then collect all <p> siblings/cousins
    that come AFTER it — this avoids nav/footer noise above the title.
    """
    h1 = soup.find("h1")
    if not h1:
        return ""

    # Walk all <p> tags in document order, keep only those after <h1>
    h1_pos = _tag_position(soup, h1)
    paragraphs = []

    for p in soup.find_all("p"):
        if _tag_position(soup, p) <= h1_pos:
            continue  # skip everything above/at the title

        text = p.get_text(separator=" ", strip=True)

        if not text or len(text) < 20:
            continue

        if any(phrase in text for phrase in _SKIP_PHRASES):
            continue

        paragraphs.append(text)

    return "\n\n".join(paragraphs)


def _extract_category(soup: BeautifulSoup) -> Optional[str]:
    """
    Quintype breadcrumb: first <a> tag whose href is a known top-level section.
    Example: <a href="/news">News</a>  or  <a href="/columns">Columns</a>
    """
    TOP_SECTIONS = ("news", "columns", "interviews", "Law-School",
                    "view-point", "dealstreet", "latest-legal-news")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip("/")          # "news" or "news/litigation"
        first_segment = href.split("/")[0]   # always "news"
        if first_segment in TOP_SECTIONS:
            return a.get_text(strip=True)    # "News" or "Litigation News"

    return None

def _tag_position(soup: BeautifulSoup, tag) -> int:
    """Returns the index of `tag` among all tags in the document."""
    return list(soup.descendants).index(tag)