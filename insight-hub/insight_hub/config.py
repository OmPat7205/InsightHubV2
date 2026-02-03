from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class IndustryConfig:
    key: str
    title: str
    rss_sources: List[str]
    include_keywords: List[str]
    exclude_keywords: List[str]

BRAND_NAME = "Insight Hub"
TIMEZONE = "America/New_York"
PUBLISH_HOUR_ET = 7  # 7:00 AM ET

# NOTE: RSS feeds change over time. These are reasonable starters.
# If a feed breaks, remove/replace it.
INDUSTRIES: Dict[str, IndustryConfig] = {
    "cybersecurity": IndustryConfig(
        key="cybersecurity",
        title="Cybersecurity Daily Intelligence Brief",
        rss_sources=[
            "https://www.cisa.gov/news.xml",
            "https://www.us-cert.gov/ncas/alerts.xml",
            "https://www.bleepingcomputer.com/feed/",
            "https://krebsonsecurity.com/feed/",
            "https://www.darkreading.com/rss.xml",
            "https://www.securityweek.com/feed/",
        ],
        include_keywords=[
            "cve", "vulnerability", "exploit", "ransomware", "breach", "malware",
            "phishing", "zero-day", "patch", "botnet", "ddos", "cisa", "incident",
            "threat", "intrusion", "data leak"
        ],
        exclude_keywords=[
            "gaming", "movie", "celebrity"
        ],
    ),
    "healthcare": IndustryConfig(
        key="healthcare",
        title="Healthcare Daily Intelligence Brief",
        rss_sources=[
            "https://www.fiercehealthcare.com/rss/xml",
            "https://www.healthcareitnews.com/home/feed",
            "https://www.cms.gov/newsroom/rss-feed",
            "https://oig.hhs.gov/rss/reports.xml",
        ],
        include_keywords=[
            "cms", "hhs", "hipaa", "reimbursement", "hospital", "clinic", "payer",
            "provider", "medicare", "medicaid", "staffing", "labor", "compliance",
            "healthcare", "ehr", "patient data"
        ],
        exclude_keywords=[
            "diet", "celebrity", "fitness influencer"
        ],
    ),
    "financial_services": IndustryConfig(
        key="financial_services",
        title="Financial Services Daily Intelligence Brief",
        rss_sources=[
            "https://www.sec.gov/news/pressreleases.rss",
            "https://www.federalreserve.gov/feeds/press_all.xml",
            "https://www.consumerfinance.gov/about-us/blog/feed/",
            "https://www.occ.treas.gov/rss/occ-news.xml",
            "https://www.ft.com/?format=rss",  # may be limited; ok to remove if noisy
        ],
        include_keywords=[
            "sec", "fed", "occ", "cfpb", "enforcement", "settlement", "fine",
            "bank", "liquidity", "capital", "stress test", "regulation",
            "fintech", "payment", "fraud", "compliance", "risk"
        ],
        exclude_keywords=[
            "sports", "celebrity", "travel"
        ],
    ),
}

# How many items to show in the brief
MAX_ITEMS_PER_BRIEF = 20
MIN_ITEMS_PER_BRIEF = 4

# Basic severity scoring thresholds
SEVERITY_HIGH_THRESHOLD = 85
SEVERITY_MED_THRESHOLD = 60
