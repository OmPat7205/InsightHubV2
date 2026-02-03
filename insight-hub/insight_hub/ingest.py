from dataclasses import dataclass
from datetime import datetime
from typing import List
import feedparser
import re


@dataclass
class Item:
    title: str
    link: str
    source: str
    published: datetime | None
    summary: str

def _parse_datetime(entry) -> datetime | None:
    # feedparser may provide: published_parsed / updated_parsed as time.struct_time
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    return None


# Fix for SSL certificate errors on Mac
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def fetch_rss_items(rss_urls: List[str]) -> List[Item]:
    items: List[Item] = []
    for url in rss_urls:
        try:
            d = feedparser.parse(url)
            if d.bozo:
                print(f"Warning: Error parsing {url}: {d.bozo_exception}")
            
            feed_title = getattr(d.feed, "title", url)
            entries = getattr(d, "entries", [])
            print(f"DEBUG: Fetched {len(entries)} entries from {url}")

            for e in entries:
                title = strip_html(getattr(e, "title", "").strip())
                link = getattr(e, "link", "").strip()
                summary_raw = (getattr(e, "summary", "") or getattr(e, "description", "") or "").strip()
                summary = strip_html(summary_raw)

                published = _parse_datetime(e)
                items.append(Item(
                    title=title,
                    link=link,
                    source=feed_title,
                    published=published,
                    summary=summary
                ))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    # de-dupe by link/title
    seen = set()
    deduped = []
    for it in items:
        key = (it.link or it.title).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return deduped

_TAG_RE = re.compile(r"<[^>]+>")

def strip_html(s: str) -> str:
    if not s:
        return ""
    return _TAG_RE.sub("", s).replace("\u00a0", " ").strip()
