import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# RSS Feeds
DEFAULT_RSS_FEEDS = [
    # Official Sources (High Priority)
    "https://openai.com/blog/rss.xml",
    "https://blog.google/rss/",
    "https://www.anthropic.com/news/rss",
    "https://ai.meta.com/blog/rss/",
    "https://blogs.microsoft.com/ai/feed/",
    "https://developer.nvidia.com/blog/feed/",
    
    # Authoritative Tech Media
    "https://venturebeat.com/category/ai/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    
    # Technical Signal (Careful with Arxiv, it floods with papers)
    "https://huggingface.co/blog/feed.xml",
    # "https://export.arxiv.org/rss/cs.AI" # Removed Arxiv to reduce noise and academic papers
]

RSS_FEEDS = os.getenv("RSS_FEEDS")
if not RSS_FEEDS:
    RSS_FEEDS = DEFAULT_RSS_FEEDS
else:
    RSS_FEEDS = RSS_FEEDS.split(",")

# Filter Settings
FRESHNESS_HOURS = int(os.getenv("FRESHNESS_HOURS", "48").strip() or "48")

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
