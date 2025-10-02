import requests
from bs4 import BeautifulSoup

def fetch(config: dict):
    items = []
    for url in config.get("urls", []):
        try:
            html = requests.get(url, timeout=20).text
        except Exception:
            continue
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("a"):
            title = (a.get_text() or "").strip()
            link = a.get("href") or ""
            if not title or not link:
                continue
            if not link.startswith("http"):
                from urllib.parse import urljoin
                link = urljoin(url, link)
            if _matches_any(title, config.get("keywords_any", [])):
                items.append({
                    "source": "nav",
                    "title": title,
                    "url": link,
                    "summary": None,
                    "published_at": None,
                    "content": None
                })
    return items

def _matches_any(text: str, keywords: list):
    t = (text or "").lower()
    return any((k or "").lower() in t for k in (keywords or [])) if keywords else True
