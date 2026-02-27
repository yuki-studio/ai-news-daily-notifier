import feedparser
import requests
from datetime import datetime
import time
from src.utils import setup_logger
from src.config import RSS_FEEDS

logger = setup_logger("rss_fetcher")

# Browser-like User-Agent to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, application/atom+xml, text/xml, */*"
}

def parse_date(date_str):
    """
    Parse date string from RSS feed into a datetime object.
    """
    try:
        # feedparser usually parses the date into a struct_time in 'published_parsed'
        # We handle this in the fetch_rss function, but this is a fallback or utility if needed.
        pass
    except Exception as e:
        logger.warning(f"Failed to parse date: {date_str}, error: {e}")
    return None

def fetch_rss_feeds():
    """
    Fetches news items from all configured RSS feeds.
    Returns a list of dictionaries containing news item details.
    """
    all_news = []
    
    for feed_url in RSS_FEEDS:
        feed_url = feed_url.strip()
        if not feed_url:
            continue
            
        logger.info(f"Fetching RSS feed: {feed_url}")
        try:
            # Use requests to fetch with headers, then parse with feedparser
            response = requests.get(feed_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
                # Continue anyway as feedparser often parses partially broken feeds
            
            for entry in feed.entries:
                # Extract publish time
                published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                if published_parsed:
                    publish_time = datetime.fromtimestamp(time.mktime(published_parsed))
                else:
                    # STRICT MODE: If no date, do NOT use current time. 
                    # Set to None so we can filter it out later or handle it as "Unknown".
                    # Using datetime.now() causes old news to appear fresh.
                    publish_time = None
                
                news_item = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                    "publish_time": publish_time,
                    "summary": entry.get("summary", "") or entry.get("description", ""),
                    "content": entry.get("content", [{"value": ""}])[0]["value"] if "content" in entry else ""
                }
                
                # Only append if we have a valid date OR if we decide to allow date-less items (currently Rejecting)
                if publish_time:
                    all_news.append(news_item)
                else:
                    logger.debug(f"Skipping item with no date: {news_item['title']}")
                
            logger.info(f"Fetched {len(feed.entries)} items from {feed_url}")
            
        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_url}: {e}")
            
    logger.info(f"Total news items fetched: {len(all_news)}")
    return all_news

if __name__ == "__main__":
    # Test the fetcher
    news = fetch_rss_feeds()
    print(f"Fetched {len(news)} items.")
    if news:
        print("Sample item:", news[0])
