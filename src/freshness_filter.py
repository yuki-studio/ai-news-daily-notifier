from datetime import datetime, timedelta
from src.utils import setup_logger
from src.config import FRESHNESS_HOURS

logger = setup_logger("freshness_filter")

def filter_fresh_news(news_list, hours=FRESHNESS_HOURS):
    """
    Filters news items that are older than the configured freshness threshold.
    Allows overriding the hours threshold for fallback logic (24h -> 72h -> 5d).
    """
    fresh_news = []
    now = datetime.now()
    cutoff_time = now - timedelta(hours=hours)
    
    logger.info(f"Filtering news older than {hours} hours (cutoff: {cutoff_time})")
    
    for item in news_list:
        publish_time = item.get("publish_time")
        
        # Ensure publish_time is offset-naive for comparison with datetime.now()
        # If it's offset-aware, convert to naive or convert 'now' to aware.
        # Simplest is to make everything naive UTC or local.
        # Feedparser usually gives UTC struct_time, converted to datetime in fetch_rss.
        # If fetch_rss provided naive datetime, we are good.
        # If fetch_rss provided aware datetime, we need to handle it.
        
        if publish_time.tzinfo is not None:
             publish_time = publish_time.replace(tzinfo=None)

        if publish_time >= cutoff_time:
            fresh_news.append(item)
        else:
            # logger.debug(f"Discarding old news: {item['title']} ({publish_time})")
            pass
            
    logger.info(f"Filtered {len(news_list) - len(fresh_news)} old items. Remaining: {len(fresh_news)}")
    return fresh_news
