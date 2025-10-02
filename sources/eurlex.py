import feedparser
from datetime import datetime

def fetch(config: dict):
    items = []
    rss_list = config.get("rss_urls", [])
    for url in rss_list:
        feed = feedparser.parse(url)
        for e in feed.entries:
            title = e.get("title", "") or ""
            link = e.get("link", "") or ""
            summary = e.get("summary", "") or ""
            published = e.get("published_parsed")
            dt = datetime(*published[:6]) if published else None
            if _matches_any(title + " " + summary, config.get("keywords_any", [])):
                items.append({
                    "source": "eurlex",
                    "title": title.strip(),
                    "url": link,
                    "summary": summary,
                    "published_at": dt,
                    "content": None
                })
    return items

def _matches_any(text: str, keywords: list):
    t = (text or "").lower()
    return any((k or "").lower() in t for k in (keywords or [])) if keywords else True
