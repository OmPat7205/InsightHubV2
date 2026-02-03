from .base import Sector
from typing import List

class Transportation(Sector):

    @property
    def name(self) -> str:
        return "Transportation & Logistics Daily Brief"

    @property
    def key(self) -> str:
        return "transportation"

    @property
    def audience(self) -> str:
        return "Supply Chain Directors, Logistics Managers, Fleet Operators, COO"

    @property
    def rss_sources(self) -> List[str]:
        return [
            "https://www.freightwaves.com/feed",
            "https://www.ttnews.com/rss.xml",  # Transport Topics
            "https://www.supplychaindive.com/feeds/news/",
            "https://logisticsviewpoints.com/feed/",
            "https://www.inboundlogistics.com/feed/",
            "https://gcaptain.com/feed/"  # Maritime for port/canal news
        ]

    @property
    def include_keywords(self) -> List[str]:
        return [
            # Core
            "3pl", "logistics", "freight", "cross-docking", "warehousing", "tms", "wms", 
            "fulfillment", "last-mile", "intermodal", "multimodal",
            # Freight Market
            "freight rates", "spot market", "truckload", "ltl", "fuel surcharge", "diesel price",
            "capacity shortage", "driver shortage", "shipping cost", "peak season",
            # Disruptions
            "port congestion", "port strike", "labor shortage", "rail strike", "weather delay",
            "panama canal", "suez canal", "border delay", "customs delay",
            # Tech
            "automation", "robotics", "ai in supply chain", "predictive analytics",
            "blockchain", "digital freight", "autonomous truck", "electric vehicle",
            # Regulations
            "dot", "fmcsa", "hours of service", "hos", "emissions", "esg", "tariffs", "trade policy",
            # Sustainability
            "sustainable logistics", "carbon emissions", "fleet electrification", "alternative fuels",
            # Trends
            "same-day delivery", "omnichannel", "e-commerce", "nearshoring", "reshoring",
            # Competitive
            "acquisition", "merger", "bankruptcy", "expansion", "partnership",
            # Niche
            "cross-dock", "hub-and-spoke", "transloading"
        ]

    @property
    def exclude_keywords(self) -> List[str]:
        return ["stock market", "earnings call", "traffic accident", "road closure"]

    @property
    def roles(self) -> List[str]:
        return ["Logistics Ops", "Supply Chain Strategy", "Compliance/Safety"]
