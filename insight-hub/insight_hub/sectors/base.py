from abc import ABC, abstractmethod
from typing import List, Dict

class Sector(ABC):
    """
    Abstract Base Class for an Industry Sector.
    Subclasses must implement:
      - name (property)
      - rss_sources (property)
      - keywords (property)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def key(self) -> str:
        """Lower-case slug used for filenames and API keys (e.g. 'cybersecurity')"""
        pass

    @property
    @abstractmethod
    def audience(self) -> str:
        pass

    @property
    @abstractmethod
    def rss_sources(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def include_keywords(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def exclude_keywords(self) -> List[str]:
        pass

    @property
    def roles(self) -> List[str]:
        """Default roles for Next Steps if not overridden"""
        return ["Leadership", "Operations", "Risk/Compliance"]
