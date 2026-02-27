from src.utils import setup_logger
from src.ai_summary import get_ai_score
from src.config import TIER1_COMPANIES, TIER2_COMPANIES, TIER1_SOURCES, TIER2_SOURCES
import re

logger = setup_logger("scoring")

# Scoring Rules (PRD v1.3)
# Base scores
SCORE_MODEL_RELEASE = 6
SCORE_MODEL_UPDATE = 5
SCORE_PRODUCT_RELEASE = 4
SCORE_PARTNERSHIP = 3

# Keyword mappings
KEYWORDS_MODEL_RELEASE = ["new model", "model release", "gpt-5", "gpt-4.5", "claude 4", "gemini 2", "llama 4"]
KEYWORDS_MODEL_UPDATE = ["update", "upgrade", "context window", "fine-tuning", "performance", "benchmark"]
KEYWORDS_PRODUCT_RELEASE = ["launch", "release", "introduce", "announce", "available now"]
KEYWORDS_PARTNERSHIP = ["partnership", "collaborate", "integration", "partner"]

def calculate_rule_score(item):
    """
    Calculates the rule-based score for a news item based on PRD v1.3.
    """
    score = 0
    title = item.get("title", "")
    summary = " ".join(item.get("summaries", []))
    source_name = item.get("source", "")
    text_to_check = (title + " " + summary).lower()
    
    # 1. Content Type Scoring
    # Check for Model Release (+6)
    if any(kw in text_to_check for kw in KEYWORDS_MODEL_RELEASE):
        score += SCORE_MODEL_RELEASE
    # Check for Model Update (+5)
    elif any(kw in text_to_check for kw in KEYWORDS_MODEL_UPDATE):
        score += SCORE_MODEL_UPDATE
    # Check for Product Release (+4)
    elif any(kw in text_to_check for kw in KEYWORDS_PRODUCT_RELEASE):
        score += SCORE_PRODUCT_RELEASE
    # Check for Partnership (+3)
    elif any(kw in text_to_check for kw in KEYWORDS_PARTNERSHIP):
        score += SCORE_PARTNERSHIP
        
    # 2. Company Tier Scoring
    # Tier 1 Companies (+3)
    if any(company.lower() in text_to_check for company in TIER1_COMPANIES):
        score += 3
    # Tier 2 Companies (+1)
    elif any(company.lower() in text_to_check for company in TIER2_COMPANIES):
        score += 1
        
    # 3. Source Tier Scoring
    # Tier 1 Sources (Official) (+4)
    # We check if the source name matches any key in TIER1_SOURCES or if the URL matches
    is_tier1_source = False
    for s_name, s_url in TIER1_SOURCES.items():
        if s_name.lower() in source_name.lower() or s_url in item.get("link", ""):
            is_tier1_source = True
            break
            
    if is_tier1_source:
        score += 4
    else:
        # Tier 2 Sources (Media) (+2)
        is_tier2_source = False
        for s_name, s_url in TIER2_SOURCES.items():
            if s_name.lower() in source_name.lower() or s_url in item.get("link", ""):
                is_tier2_source = True
                break
        if is_tier2_source:
            score += 2
            
    # 4. Technical Details Bonus (+2)
    # Heuristic: Check for numbers/metrics in text
    if re.search(r'\d+(\.\d+)?%', text_to_check) or re.search(r'\d+x', text_to_check) or "token" in text_to_check:
        score += 2
        
    # Normalize score to 0-100 scale roughly for combination with AI score
    # Max rule score approx: 6 + 3 + 4 + 2 = 15. 
    # We scale it up to weigh against AI score (0-100). 
    # Let's say max reasonable rule score is 20. 20 * 5 = 100.
    normalized_score = min(score * 6, 100)
    
    return normalized_score

def score_news(news_list):
    """
    Applies scoring to a list of news items.
    """
    logger.info(f"Scoring {len(news_list)} items")
    
    for item in news_list:
        rule_score = calculate_rule_score(item)
        item["rule_score"] = rule_score
        
        # Get AI Score
        ai_score = get_ai_score(item)
        item["ai_score"] = ai_score
        
        # Final Score: Rule * 0.5 + AI * 0.5 (Balanced approach)
        item["final_score"] = rule_score * 0.5 + ai_score * 0.5
        
        logger.debug(f"Scored '{item['title'][:30]}...': Rule={rule_score}, AI={ai_score}, Final={item['final_score']}")
        
    return news_list
