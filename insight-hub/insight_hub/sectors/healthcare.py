from .base import Sector
from typing import List

class Healthcare(Sector):

    @property
    def name(self) -> str:
        return "Healthcare Daily Intelligence Brief"

    @property
    def key(self) -> str:
        return "healthcare"

    @property
    def audience(self) -> str:
        return "Healthcare executives, Clinical Operations, Compliance & Risk teams"

    @property
    def rss_sources(self) -> List[str]:
        return [
            "https://www.fiercehealthcare.com/rss/xml",
            "https://www.healthcareitnews.com/home/feed",
            "https://www.cms.gov/newsroom/rss-feed",
            "https://oig.hhs.gov/rss/reports.xml",
        ]

    @property
    def include_keywords(self) -> List[str]:
        return [
            "cms", "hhs", "hipaa", "reimbursement", "hospital", "clinic", "payer",
            "provider", "medicare", "medicaid", "staffing", "labor", "compliance",
            "healthcare", "ehr", "patient data"
        ]

    @property
    def exclude_keywords(self) -> List[str]:
        return ["diet", "celebrity", "fitness influencer"]

    @property
    def roles(self) -> List[str]:
        return ["Clinical Ops", "IT/SecOps", "Compliance/Legal"]
