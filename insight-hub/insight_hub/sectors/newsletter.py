from .base import Sector
from typing import List

class Newsletter(Sector):

    @property
    def name(self) -> str:
        return "AI Daily Briefing"

    @property
    def key(self) -> str:
        return "newsletter"

    @property
    def audience(self) -> str:
        return "Developers, Tech Leaders, AI Researchers, Business Executives"

    @property
    def rss_sources(self) -> List[str]:
        return [
            "https://openai.com/news/rss.xml",
            "https://research.google/blog/rss",
            "https://techcrunch.com/category/artificial-intelligence/feed",
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "https://www.wired.com/feed/tag/ai/latest/rss",
            "https://www.technologyreview.com/feed/topic/artificial-intelligence",
            "https://blogs.microsoft.com/ai/feed/",
            "https://venturebeat.com/category/ai/feed/",
            "https://news.mit.edu/rss/topic/artificial-intelligence2",
            "https://www.artificialintelligence-news.com/feed/",
        ]

    @property
    def include_keywords(self) -> List[str]:
        return [
            "llm", "generative ai", "neural network", "transformer", "openai", 
            "google deepmind", "anthropic", "mistral", "llama", "gpu", "nvidia", 
            "agi", "machine learning", "computer vision", "nlp", "chatbot",
            "chatgpt", "gemini", "copilot", "hugging face", "open source ai",
            "ai regulation", "ai safety", "ai ethics", "robotics", "automation",
            "reasoning model", "agentic ai", "foundation model", "sora", "claude"
        ]

    @property
    def exclude_keywords(self) -> List[str]:
        return ["crypto", "blockchain", "nft", "metaverse", "gaming", "celebrity"]

    @property
    def roles(self) -> List[str]:
        return ["CTO", "AI Engineer", "Product Manager", "Research Scientist"]
