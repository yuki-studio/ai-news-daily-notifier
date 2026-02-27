import sys
import argparse
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
    parser = argparse.ArgumentParser(description="AI News Notifier")
    parser.add_argument("--ignore-freshness", action="store_true", help="Ignore time filters (for testing/backfill)")
    args = parser.parse_args()

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
    target_count = 5
    selected_news = []
    
    if args.ignore_freshness:
        logger.info("TEST MODE: Ignoring freshness filter. Processing ALL fetched news.")
        selected_news = all_news
    else:
        time_windows = [24, 72, 120]
        
        for hours in time_windows:
            logger.info(f"Trying time window: {hours} hours")
            fresh_news = filter_fresh_news(all_news, hours=hours)
            
            if not fresh_news:
                logger.info(f"No fresh news found within {hours}h.")
                continue
                
            # 3. Deduplicate (Moved inside loop to process smaller chunks efficiently, or can be done after)
            # Actually, deduplication should be done on the fresh set
            unique_news = deduplicate_news(fresh_news)
            
            # 4. Merge
            merged_news = merge_news_items(unique_news)
            
            # 5. Score
            scored_news = score_news(merged_news)
            
            # 6. Rank
            ranked_news = rank_news(scored_news)
            
            # Check if we have enough high-quality news
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
        
    # If ignoring freshness, we still need to run the pipeline steps (Deduplicate -> Rank)
    if args.ignore_freshness:
        unique_news = deduplicate_news(selected_news)
        merged_news = merge_news_items(unique_news)
        scored_news = score_news(merged_news)
        ranked_news = rank_news(scored_news)
        selected_news = ranked_news

    # Take top N
    top_news = selected_news[:target_count]
        
    # 7. Generate Summaries
    logger.info(f"Generating summaries for {len(top_news)} items")
    summarized_news = []
    for item in top_news:
        try:
            summary_data = generate_summary(item)
            
            # Merge summary data with original item data
            final_item = {
                **summary_data,
                "links": item.get("links", []),
                "original_sources": item.get("sources", []), 
                "original_title": item.get("title"),
                "publish_date": item.get("publish_time").strftime("%Y-%m-%d %H:%M") # Format for Feishu
            }
            
            # Fallback logic for URL and Source Name
            if not final_item.get("url") or final_item.get("url") == "":
                 if item.get("link"):
                     final_item["url"] = item["link"]
                 elif item.get("links"):
                     final_item["url"] = item["links"][0]
            
            if not final_item.get("source_name") or final_item.get("source_name") == "Unknown":
                 if item.get("source"):
                     final_item["source_name"] = item["source"]
                 elif item.get("sources"):
                     final_item["source_name"] = item["sources"][0]

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
