from difflib import SequenceMatcher
from src.utils import setup_logger
from src.config import TIER1_SOURCES, TIER2_SOURCES

logger = setup_logger("merge_news")

MERGE_SIMILARITY_THRESHOLD = 0.7

def is_similar(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio() > MERGE_SIMILARITY_THRESHOLD

def get_source_priority(source_name, link):
    """
    Returns a priority score for a source (lower is better).
    1: Tier 1 (Official)
    2: Reuters
    3: Bloomberg
    4: TechCrunch
    5: Tier 2 (Other Media)
    6: Others
    """
    s_lower = source_name.lower()
    l_lower = link.lower()
    
    # 1. Official Sources
    for name, url in TIER1_SOURCES.items():
        if name.lower() in s_lower or url in link:
            return 1
            
    # 2. Reuters
    if "reuters" in s_lower or "reuters.com" in l_lower:
        return 2
        
    # 3. Bloomberg
    if "bloomberg" in s_lower or "bloomberg.com" in l_lower:
        return 3
        
    # 4. TechCrunch
    if "techcrunch" in s_lower or "techcrunch.com" in l_lower:
        return 4
        
    # 5. Tier 2 (Other Media)
    for name, url in TIER2_SOURCES.items():
        if name.lower() in s_lower or url in link:
            return 5
            
    # 6. Others
    return 6

def merge_news_items(news_list):
    """
    Merges news items that are about the same topic.
    Selects the best title and link based on source priority.
    """
    merged_news = []
    
    logger.info(f"Starting merge process on {len(news_list)} items")
    
    # Sort by publish time desc so we prioritize latest as the "base" for loop
    sorted_news = sorted(news_list, key=lambda x: x['publish_time'], reverse=True)
    
    while sorted_news:
        base_item = sorted_news.pop(0)
        
        # Initialize group
        group = [base_item]
        
        # Find similar items
        remaining_news = []
        for item in sorted_news:
            if is_similar(base_item["title"], item["title"]):
                group.append(item)
            else:
                remaining_news.append(item)
        
        sorted_news = remaining_news
        
        # Determine best item in group based on Source Priority
        # Sort group by priority (asc) then by time (desc)
        best_item = sorted(group, key=lambda x: (get_source_priority(x["source"], x["link"]), -x["publish_time"].timestamp()))[0]
        
        # Construct merged item
        merged_item = {
            "title": best_item["title"], # Use title from best source
            "link": best_item["link"],   # Use link from best source
            "source": best_item["source"], # Use source name from best source
            "publish_time": max(item["publish_time"] for item in group), # Use latest time
            "sources": list(set(item["source"] for item in group)),
            "links": list(set(item["link"] for item in group)),
            "summaries": [item["summary"] for item in group],
            "contents": [item.get("content", "") for item in group],
            "original_items": group
        }
        
        merged_news.append(merged_item)
        
    logger.info(f"Merge complete. Resulted in {len(merged_news)} items from {len(news_list)} original items.")
    return merged_news
