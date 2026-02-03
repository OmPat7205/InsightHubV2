import re
from datetime import datetime
from typing import List
from .ingest import Item
from .config import (
    MAX_ITEMS_PER_BRIEF,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_MED_THRESHOLD,
)

import re
from collections import defaultdict
from typing import List, Dict

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()

def in_window(item: Item, start: datetime, end: datetime) -> bool:
    # If no published time, keep it but later rank it lower.
    if item.published is None:
        return True
    # item.published is naive datetime; treat it as "unknown timezone".
    # We use it only as rough filter: keep if within range using naive comparisons.
    return start.replace(tzinfo=None) <= item.published <= end.replace(tzinfo=None)

def keyword_match_score(text: str, keywords: List[str]) -> int:
    t = _norm(text)
    score = 0
    for kw in keywords:
        if kw.lower() in t:
            score += 1
    return score

def severity_score(item: Item, include_keywords: List[str]) -> int:
    """
    Simple heuristic scoring. You’ll upgrade this later.
    Higher score = more urgent / actionable.
    """
    t = _norm(item.title + " " + item.summary)

    high_markers = ["actively exploited", "zero-day", "ransomware", "breach", "critical", "remote code execution"]
    med_markers  = ["patch", "vulnerability", "enforcement", "fine", "settlement", "incident", "advisory", "recall"]

    score = 0
    score += 10 * keyword_match_score(t, include_keywords)
    score += 25 * sum(1 for m in high_markers if m in t)
    score += 12 * sum(1 for m in med_markers if m in t)

    # Slight penalty for missing link/title
    if not item.link:
        score -= 10
    if not item.title:
        score -= 10

    # Clamp
    return max(0, min(100, score))

def assign_severity(score: int) -> str:
    if score >= SEVERITY_HIGH_THRESHOLD:
        return "High"
    if score >= SEVERITY_MED_THRESHOLD:
        return "Medium"
    return "Low"

def filter_and_rank(
    items: List[Item],
    start: datetime,
    end: datetime,
    include_keywords: List[str],
    exclude_keywords: List[str],
) -> List[dict]:
    ex = [_norm(x) for x in exclude_keywords]
    filtered = []
    for it in items:
        if not in_window(it, start, end):
            continue
        text = _norm(it.title + " " + it.summary)
        if any(bad in text for bad in ex):
            continue

        # must match at least 1 include keyword to reduce noise
        if keyword_match_score(text, include_keywords) == 0:
            continue

        score = severity_score(it, include_keywords)
        filtered.append({
            "title": it.title,
            "link": it.link,
            "source": it.source,
            "published": it.published,
            "summary": it.summary,
            "score": score,
            "severity": assign_severity(score),
        })

    # rank: higher score first, then newest
    def sort_key(x):
        pub = x["published"] or datetime(1970, 1, 1)
        return (x["score"], pub)

    filtered.sort(key=sort_key, reverse=True)
    return filtered[:MAX_ITEMS_PER_BRIEF]




def _norm_title(s: str) -> str:
    """Normalize titles for dedupe: lowercase, strip punctuation/extra spaces."""
    s = (s or "").lower().strip()
    s = re.sub(r"https?://\S+", "", s)         # remove URLs
    s = re.sub(r"[^a-z0-9\s]+", " ", s)        # remove punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s

def apply_quality_controls(items: List[Dict], max_per_source: int = 2) -> List[Dict]:
    """
    Enforces:
      - De-dupe by normalized title
      - Source diversity cap (max N items per source)
    Keeps order (assumes items already ranked best->worst).
    """
    if not items:
        return []

    seen_titles = set()
    per_source = defaultdict(int)
    out: List[Dict] = []

    for it in items:
        title = it.get("title", "") or ""
        norm = _norm_title(title)
        if not norm:
            continue

        # De-dupe
        if norm in seen_titles:
            continue
        seen_titles.add(norm)

        # Source cap
        src = (it.get("source", "") or "Unknown").strip()
        if per_source[src] >= max_per_source:
            continue
        per_source[src] += 1

        out.append(it)

    return out
