from .base import Sector
from typing import List

class Cybersecurity(Sector):

    @property
    def name(self) -> str:
        return "Cybersecurity Daily Intelligence Brief"

    @property
    def key(self) -> str:
        return "cybersecurity"

    @property
    def audience(self) -> str:
        return "Security leaders (CISO), IT decision-makers, Risk & Compliance teams"

    @property
    def rss_sources(self) -> List[str]:
        return [
            "https://www.cisa.gov/news.xml",
            "https://www.us-cert.gov/ncas/alerts.xml",
            "https://www.bleepingcomputer.com/feed/",
            "https://krebsonsecurity.com/feed/",
            "https://www.darkreading.com/rss.xml",
            "https://www.securityweek.com/feed/",
            "https://feeds.feedburner.com/TheHackersNews",
        ]

    @property
    def include_keywords(self) -> List[str]:
        return [
            "cve", "vulnerability", "exploit", "ransomware", "breach", "malware",
            "phishing", "zero-day", "patch", "botnet", "ddos", "cisa", "incident",
            "threat", "intrusion", "data leak", "supply chain", "api security",
            "cloud security", "identity", "mfa", "authentication", "apt", "nation-state",
            "ai", "llm", "injection"
        ]

    @property
    def exclude_keywords(self) -> List[str]:
        return ["gaming", "movie", "celebrity"]

    @property
    def roles(self) -> List[str]:
        return ["IT Ops", "SecOps", "GRC/Legal"]
