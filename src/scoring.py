from src.utils import setup_logger
from src.ai_summary import get_ai_score
import re

logger = setup_logger("scoring")

# Scoring Rules
KEYWORDS_MODEL_UPDATE = ["GPT", "Claude", "Gemini", "Llama", "DeepSeek", "model release", "new model"]
KEYWORDS_NEW_PRODUCT = ["launch", "release", "introduce", "new product"]
KEYWORDS_TECH_BREAKTHROUGH = ["video model", "multimodal", "reasoning", "agent"]

OFFICIAL_SOURCES = ["OpenAI", "Google", "Anthropic", "Meta", "Microsoft", "NVIDIA"]

def calculate_rule_score(item):
    """
    Calculates the rule-based score for a news item.
    """
    score = 0
    title = item.get("title", "")
    summary = " ".join(item.get("summaries", []))
    text_to_check = (title + " " + summary).lower()
    
    # 1. Model Update (+40)
    for kw in KEYWORDS_MODEL_UPDATE:
        if kw.lower() in text_to_check:
            score += 40
            break # Apply once
            
    # 2. New Product (+25)
    for kw in KEYWORDS_NEW_PRODUCT:
        if kw.lower() in text_to_check:
            score += 25
            break
            
    # 3. Tech Breakthrough (+20)
    for kw in KEYWORDS_TECH_BREAKTHROUGH:
        if kw.lower() in text_to_check:
            score += 20
            break
            
    # 4. Source Score
    sources = item.get("sources", [])
    is_official = False
    for source in sources:
        # Simple string matching for source name
        if any(official.lower() in source.lower() for official in OFFICIAL_SOURCES):
            is_official = True
            break
    
    # Boost Official Sources significantly
    if is_official:
        score += 30 # Increased from 15 to 30
    else:
        # Penalize unknown sources slightly if needed, or just keep low base
        score += 5
        
    # Check for "Arxiv" in source or link and Penalize
    # We want industry news, not just papers
    if any("arxiv" in s.lower() for s in sources) or "arxiv.org" in item.get("link", "").lower():
        score -= 20 # Penalize Arxiv papers unless they are huge breakthroughs
        
    # 5. Multiple Sources
    num_sources = len(sources)
    if num_sources >= 3:
        score += 20
    elif num_sources == 2:
        score += 10
        
    return min(score, 100) # Cap at 100 for rule score (though PRD doesn't explicitly say cap rule score, but final score formula implies normalized inputs)

def score_news(news_list):
    """
    Applies scoring to a list of news items.
    Calculates Rule Score and AI Score, then computes Final Score.
    """
    logger.info(f"Scoring {len(news_list)} items")
    
    for item in news_list:
        rule_score = calculate_rule_score(item)
        item["rule_score"] = rule_score
        
        # Get AI Score
        ai_score = get_ai_score(item)
        item["ai_score"] = ai_score
        
        # Final Score: Rule * 0.4 + AI * 0.6
    # Adjusted weights: Rely more on Rules for source filtering
    item["final_score"] = rule_score * 0.5 + ai_score * 0.5
        
        logger.debug(f"Scored '{item['title'][:30]}...': Rule={rule_score}, AI={ai_score}, Final={item['final_score']}")
        
    return news_list
