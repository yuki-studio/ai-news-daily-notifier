import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# RSS Feeds Configuration (PRD v1.3)

# Tier 1: Official Sources (Priority +4)
TIER1_SOURCES = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Google": "https://blog.google/rss/",
    "Anthropic": "https://www.anthropic.com/news/rss",
    "Meta": "https://ai.meta.com/blog/rss/",
    "Microsoft": "https://blogs.microsoft.com/ai/feed/",
    "NVIDIA": "https://developer.nvidia.com/blog/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml" # Treated as Tier 1 for technical community
}

# Tier 2: Authoritative Media (Priority +2)
TIER2_SOURCES = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/", # PRD v1.3 puts VB in Tier 3, but let's keep it here for now or separate
}

# Tier 3: Cautious Sources (Max 1 item)
TIER3_SOURCES = {
    # Add more if needed, e.g. Wired
}

# Combine all feeds
DEFAULT_RSS_FEEDS = list(TIER1_SOURCES.values()) + list(TIER2_SOURCES.values()) + list(TIER3_SOURCES.values())

RSS_FEEDS = os.getenv("RSS_FEEDS")
if not RSS_FEEDS:
    RSS_FEEDS = DEFAULT_RSS_FEEDS
else:
    RSS_FEEDS = RSS_FEEDS.split(",")

# Important Companies (PRD v1.3)
TIER1_COMPANIES = ["OpenAI", "Google", "DeepMind", "Anthropic", "Meta", "Microsoft", "Alibaba", "Baidu", "Tencent", "ByteDance", "Zhipu"]
TIER2_COMPANIES = ["xAI", "NVIDIA", "Amazon", "Apple", "Mistral", "Perplexity", "Midjourney", "Stability"]

# Filter Settings
FRESHNESS_HOURS = int(os.getenv("FRESHNESS_HOURS", "24").strip() or "24") # Default 24h as per v1.3

# Deduplication Settings
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8").strip() or "0.8")

# Scoring Settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").strip().strip('"').strip("'").lower() # openai or deepseek
AI_API_KEY = os.getenv("AI_API_KEY", "").strip().strip('"').strip("'")
AI_BASE_URL = os.getenv("AI_BASE_URL", "").strip().strip('"').strip("'")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o").strip().strip('"').strip("'") # or deepseek-chat

# Ranking Settings
TOP_N = int(os.getenv("TOP_N", "5").strip() or "5")

# Feishu Settings
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "").strip().strip('"').strip("'")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
