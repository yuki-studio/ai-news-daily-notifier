import sys
from src.config import AI_API_KEY, AI_PROVIDER, AI_MODEL, AI_BASE_URL, FEISHU_WEBHOOK
from src.utils import setup_logger
from src.fetch_rss import fetch_rss_feeds
from src.freshness_filter import filter_fresh_news
from src.deduplicate import deduplicate_news
from src.merge_news import merge_news_items
from src.scoring import score_news
from src.ranking import rank_news
from src.ai_summary import generate_summary
from src.feishu_sender import send_to_feishu

logger = setup_logger("main")

def main():
    logger.info("Starting AI News Notifier Pipeline")
    
    # Log configuration (masking sensitive data)
    masked_key = f"{AI_API_KEY[:4]}...{AI_API_KEY[-4:]}" if AI_API_KEY and len(AI_API_KEY) > 8 else "NOT_SET"
    logger.info(f"Configuration: Provider={AI_PROVIDER}, Model={AI_MODEL}, BaseURL={AI_BASE_URL}, API_KEY={masked_key}")
    logger.info(f"Feishu Webhook set: {'Yes' if FEISHU_WEBHOOK else 'No'}")

    # 1. Fetch
    all_news = fetch_rss_feeds()
    if not all_news:
        logger.info("No news fetched. Exiting.")
        return

    # 2. Filter Freshness (Tiered Strategy: 24h -> 72h -> 120h)
    time_windows = [24, 72, 120]
    target_count = 5
    selected_news = []
    
    for hours in time_windows:
        logger.info(f"Trying time window: {hours} hours")
        fresh_news = filter_fresh_news(all_news, hours=hours)
        
        if not fresh_news:
            logger.info(f"No fresh news found within {hours}h.")
            continue
            
        # 3. Deduplicate
        unique_news = deduplicate_news(fresh_news)
        
        # 4. Merge
        merged_news = merge_news_items(unique_news)
        
        # 5. Score
        scored_news = score_news(merged_news)
        
        # 6. Rank
        ranked_news = rank_news(scored_news)
        
        # Check if we have enough high-quality news
        # We can define a threshold score if needed, but for now just count
        if len(ranked_news) >= target_count:
            selected_news = ranked_news
            logger.info(f"Found {len(selected_news)} items within {hours}h window. Stopping search.")
            break
        else:
            logger.info(f"Only found {len(ranked_news)} items within {hours}h window. Expanding search...")
            # If we are at the last window, just take what we have
            if hours == time_windows[-1]:
                selected_news = ranked_news

    if not selected_news:
        logger.info("No news found even after expanding time window. Exiting.")
        return
        
    # Take top N
    top_news = selected_news[:target_count]
        
    # 7. Generate Summaries
    logger.info(f"Generating summaries for {len(top_news)} items")
    summarized_news = []
    for item in top_news:
        try:
            summary_data = generate_summary(item)
            
            # Merge summary data with original item data
            # We want to keep the link and original sources
            final_item = {
                **summary_data,
                "links": item.get("links", []),
                "original_sources": item.get("sources", []), # rename to avoid conflict if summary has source_name
                "original_title": item.get("title")
            }
            # Fallback for source_name and url if AI failed to extract them OR if we want to enforce best source
            # PRD v1.3: Use the best source link selected by merge_news
            if item.get("link"):
                 final_item["url"] = item["link"]
            if item.get("source"):
                 final_item["source_name"] = item["source"]
                 
            # Fallback if still empty
            if not final_item.get("url") and final_item.get("links"):
                 final_item["url"] = final_item["links"][0]
            if not final_item.get("source_name") and final_item.get("original_sources"):
                 final_item["source_name"] = final_item["original_sources"][0]

            summarized_news.append(final_item)
        except Exception as e:
            logger.error(f"Error processing summary for item '{item.get('title')}': {e}")
            
    # 8. Send to Feishu
    if summarized_news:
        send_to_feishu(summarized_news)
    else:
        logger.warning("No summaries generated. Nothing to send.")
        
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
