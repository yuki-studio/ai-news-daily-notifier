import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# RSS Feeds Configuration (PRD v1.5)

# Tier 1: Official Sources (Priority +4)
TIER1_SOURCES = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Google": "https://blog.google/rss/",
    "Anthropic": "https://www.anthropic.com/news/rss",
    "Meta": "https://ai.meta.com/blog/rss/",
    "Microsoft": "https://blogs.microsoft.com/ai/feed/",
    "NVIDIA": "https://developer.nvidia.com/blog/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "GitHub": "https://github.blog/feed/",
    "AWS": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "DeepSeek": "https://api.deepseek.com/feed", # Placeholder
    "Aliyun": "https://developer.aliyun.com/rss", # Placeholder
}

# Tier 2: Authoritative Media (Priority +2)
TIER2_SOURCES = {
    "Reuters": "https://www.reuters.com/arc/outboundfeeds/v2/?outputType=xml&video=true&namedItemId=technology", # Tech
    "Bloomberg": "https://feeds.bloomberg.com/technology/news.xml",
    "Financial Times": "https://www.ft.com/technology?format=rss",
    "The Information": "https://www.theinformation.com/feed",
}

# Tier 3: Cautious Sources (Max 1 item)
TIER3_SOURCES = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Wired": "https://www.wired.com/feed/category/ai/latest/rss",
}

# Combine all feeds
DEFAULT_RSS_FEEDS = list(TIER1_SOURCES.values()) + list(TIER2_SOURCES.values()) + list(TIER3_SOURCES.values())

RSS_FEEDS = os.getenv("RSS_FEEDS")
if not RSS_FEEDS:
    RSS_FEEDS = DEFAULT_RSS_FEEDS
else:
    RSS_FEEDS = RSS_FEEDS.split(",")

# Company Priorities (PRD v1.5)
# P0 Global
P0_GLOBAL = ["OpenAI", "Google", "Microsoft", "Anthropic", "Meta"]
# P0 China
P0_CHINA = ["Baidu", "Alibaba", "Tencent", "Huawei", "ByteDance"]

# P1 Global
P1_GLOBAL = ["Nvidia", "AWS", "Apple", "xAI", "Mistral", "Adobe", "Stability AI"]
# P1 China
P1_CHINA = ["DeepSeek", "Zhipu", "Moonshot", "MiniMax", "StepFun", "Baichuan", "01.AI", "SenseTime", "iFlytek"]

# P2 China
P2_CHINA = ["Cambricon", "Moore Threads", "MetaX", "Xiao-i"]

# Combined Lists for Scoring
TIER1_COMPANIES = P0_GLOBAL + P0_CHINA
TIER2_COMPANIES = P1_GLOBAL + P1_CHINA
TIER3_COMPANIES = P2_CHINA

# Filter Settings
FRESHNESS_HOURS = int(os.getenv("FRESHNESS_HOURS", "24").strip() or "24")

# Deduplication Settings
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8").strip() or "0.8")

# Scoring Settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").strip().strip('"').strip("'").lower() # openai or deepseek
AI_API_KEY = os.getenv("AI_API_KEY", "").strip().strip('"').strip("'")
AI_BASE_URL = os.getenv("AI_BASE_URL", "").strip().strip('"').strip("'")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o").strip().strip('"').strip("'") 

# Ranking Settings
TOP_N = int(os.getenv("TOP_N", "5").strip() or "5")

# Feishu Settings
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "").strip().strip('"').strip("'")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")