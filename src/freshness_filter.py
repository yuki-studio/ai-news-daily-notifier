from datetime import datetime, timedelta
from src.utils import setup_logger
from src.config import FRESHNESS_HOURS

logger = setup_logger("freshness_filter")

def filter_fresh_news(news_list, hours=FRESHNESS_HOURS):
    """
    Filters news items using 'Relative Freshness'.
    1. Find the latest timestamp in the entire list (max_publish_time).
    2. Keep items within 'hours' of that max_publish_time.
    
    This solves the "System Time vs Real Time" paradox where 
    system time is 2026 but RSS feeds have 2025 data.
    """
    if not news_list:
        return []
        
    fresh_news = []
    
    # Normalize timezones first
    valid_items = []
    for item in news_list:
        publish_time = item.get("publish_time")
        if not publish_time:
            continue
        if publish_time.tzinfo is not None:
            item["publish_time"] = publish_time.replace(tzinfo=None)
        valid_items.append(item)
        
    if not valid_items:
        return []

    # Find the latest time in the feed
    max_publish_time = max(item["publish_time"] for item in valid_items)
    
    # Calculate cutoff relative to the LATEST item found, NOT system clock
    cutoff_time = max_publish_time - timedelta(hours=hours)
    
    logger.info(f"Relative Freshness: Latest item is from {max_publish_time}. Filtering older than {hours}h (cutoff: {cutoff_time})")
    
    for item in valid_items:
        if item["publish_time"] >= cutoff_time:
            fresh_news.append(item)
            
    logger.info(f"Filtered {len(news_list) - len(fresh_news)} old items. Remaining: {len(fresh_news)}")
    return fresh_news
