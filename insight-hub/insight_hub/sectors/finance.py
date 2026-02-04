from .base import Sector
from typing import List

class FinancialServices(Sector):

    @property
    def name(self) -> str:
        return "Financial Services Daily Intelligence Brief"

    @property
    def key(self) -> str:
        return "financial_services"

    @property
    def audience(self) -> str:
        return "Risk leaders (CRO), Compliance teams, Finance & Regulatory stakeholders"

    @property
    def rss_sources(self) -> List[str]:
        return [
            "https://www.sec.gov/news/pressreleases.rss",
            "https://www.federalreserve.gov/feeds/press_all.xml",
            "https://www.consumerfinance.gov/about-us/blog/feed/",
            "https://www.occ.treas.gov/rss/occ-news.xml",
            "https://www.ft.com/?format=rss",
            "https://www.cnbc.com/id/10000664/device/rss/rss.html", # Finance
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.wsj.com/xml/rss/3_7031.xml", # Markets
            "https://cointelegraph.com/rss"
        ]

    @property
    def include_keywords(self) -> List[str]:
        return [
            "sec", "fed", "occ", "cfpb", "enforcement", "settlement", "fine",
            "bank", "liquidity", "capital", "stress test", "regulation",
            "fintech", "payment", "fraud", "compliance", "risk",
            "interest rate", "inflation", "cpi", "fomc", "crypto regulation",
            "stablecoin", "cbdc", "basel iii", "dodd-frank", "anti-money laundering", "aml", "kyc"
        ]

    @property
    def exclude_keywords(self) -> List[str]:
        return ["sports", "celebrity", "travel"]

    @property
    def roles(self) -> List[str]:
        return ["Finance/Treasury", "Risk/Controls", "Compliance/Legal"]
