from src.utils import setup_logger
from src.ai_summary import get_ai_score
from src.config import TIER1_COMPANIES, TIER2_COMPANIES, TIER3_COMPANIES, TIER1_SOURCES, TIER2_SOURCES
import re

logger = setup_logger("scoring")

# Scoring Rules (PRD v1.5)

# News Types (One of these is required)
TYPE_PRODUCT_MODEL_RELEASE = 10 # Type 1
TYPE_CAPABILITY_STRATEGY = 8    # Type 2
TYPE_INDUSTRY_EVENT = 6         # Type 3

# Event Strength Keywords (Must contain at least one)
KEYWORDS_EVENT_STRENGTH = [
    "launch", "release", "introduce", "announce", "update", "upgrade", 
    "open", "provide", "available", "deploy", "rollout", "ship", "debut"
]

# Marketing Keywords (Negative Filter)
KEYWORDS_MARKETING = [
    "significant improvement", "significantly improve", 
    "revolutionary", "revolutionize", 
    "next generation", "next-gen",
    "industry leading", "industry-leading",
    "game changer", "game-changer"
]

# Landing Signal Keywords (Must contain at least one)
KEYWORDS_LANDING_ENTRY = ["console", "dashboard", "portal", "docs", "documentation", "api reference", "playground"]
KEYWORDS_LANDING_TECH = ["api", "sdk", "parameter", "function calling", "json mode", "context window", "latency", "throughput", "fine-tuning"]
KEYWORDS_LANDING_COMMERCIAL = ["price", "pricing", "cost", "tier", "plan", "enterprise", "quota", "rate limit"]

# Local/Regional Keywords (Hard Filter)
KEYWORDS_LOCAL_ONLY = [
    "massachusetts", "boston", "india", "japan", "korea", "france", "germany", "uk", "london", 
    "california", "san francisco", "training program", "initiative for", "residents", "local",
    "government of", "ministry of", "state of", "province", "city of"
]

def calculate_rule_score(item):
    """
    Calculates the rule-based score for a news item based on PRD v1.5.
    """
    score = 0
    title = item.get("title", "")
    summary = " ".join(item.get("summaries", []))
    source_name = item.get("source", "")
    text_to_check = (title + " " + summary).lower()
    
    # --- 0. Local/Regional Filter (Hard Reject) ---
    # Reject if it's purely a local initiative (e.g., "OpenAI for India", "Training for Massachusetts")
    # UNLESS it involves a Global Product Launch or Major Policy (but usually those won't have 'residents' in title)
    if any(kw in text_to_check for kw in KEYWORDS_LOCAL_ONLY):
        # Double check: Is it a global product rollout that just happens to mention a region?
        # e.g. "ChatGPT now available in Italy" -> Maybe keep? 
        # But "Training for residents" -> Reject.
        if "training" in text_to_check or "initiative" in text_to_check or "residents" in text_to_check:
             logger.debug(f"Rejecting '{title[:20]}...': Local/Regional initiative")
             return 0
    
    # --- 1. Event Strength Check (Hard Filter) ---
    has_event_strength = any(kw in text_to_check for kw in KEYWORDS_EVENT_STRENGTH)
    if not has_event_strength:
        logger.debug(f"Rejecting '{title[:20]}...': Weak event strength")
        return 0 # Reject R101_WEAK_EVENT

    # --- 2. Marketing Language Check (Negative Filter) ---
    # Reject if marketing language exists BUT no specific metrics/functions are found
    has_marketing = any(kw in text_to_check for kw in KEYWORDS_MARKETING)
    has_substance = re.search(r'\d+(\.\d+)?%|\d+x|\d+[kKmMbB]|\$\d+', text_to_check) or \
                    any(kw in text_to_check for kw in ["api", "parameter", "function", "mode", "feature"])
    
    if has_marketing and not has_substance:
        logger.debug(f"Rejecting '{title[:20]}...': Marketing fluff")
        return 0 # Reject R102_MARKETING_LANGUAGE

    # --- 3. Landing Signal Check (Hard Filter) ---
    has_entry = any(kw in text_to_check for kw in KEYWORDS_LANDING_ENTRY)
    has_tech = any(kw in text_to_check for kw in KEYWORDS_LANDING_TECH)
    has_commercial = any(kw in text_to_check for kw in KEYWORDS_LANDING_COMMERCIAL)
    
    if not (has_entry or has_tech or has_commercial):
        # Allow if it's a Type 1 (New Product) even without explicit signals in text, 
        # as the event itself implies entry point usually.
        # But PRD says "Otherwise reject R093". 
        # We will be strict but allow official sources to pass easier.
        is_official = any(s_url in item.get("link", "") for s_url in TIER1_SOURCES.values())
        if not is_official:
             logger.debug(f"Rejecting '{title[:20]}...': No landing signal")
             return 0

    # --- 4. News Value Scoring (Type 1/2/3) ---
    # Heuristic detection
    if any(kw in text_to_check for kw in ["new model", "new product", "launch", "release"]):
        score += TYPE_PRODUCT_MODEL_RELEASE
    elif any(kw in text_to_check for kw in ["update", "upgrade", "api", "capability", "strategy", "price"]):
        score += TYPE_CAPABILITY_STRATEGY
    else:
        score += TYPE_INDUSTRY_EVENT # Fallback, lowest value

    # --- 5. Company Priority Scoring ---
    # Only give points if it is a Tier 1/2 company.
    # CRITICAL: If the company is NOT in Tier 1 or Tier 2, apply a PENALTY.
    # This filters out "Genmab" or random partners unless the event is huge.
    
    is_tier1 = any(c.lower() in text_to_check for c in TIER1_COMPANIES)
    is_tier2 = any(c.lower() in text_to_check for c in TIER2_COMPANIES)
    
    if is_tier1:
        score += 5 # P0
    elif is_tier2:
        score += 3 # P1
    elif any(c.lower() in text_to_check for c in TIER3_COMPANIES):
        score += 1 # P2
    else:
        # If not a known major AI company, penalize heavily (-10)
        logger.debug(f"Penalizing '{title[:20]}...': No major AI company found")
        score -= 10
             
    # --- 6. Source Tier Scoring ---
    is_tier1_source = False
    for s_name, s_url in TIER1_SOURCES.items():
        if s_name.lower() in source_name.lower() or s_url in item.get("link", ""):
            is_tier1_source = True
            break
            
    if is_tier1_source:
        score += 5
    else:
        is_tier2_source = False
        for s_name, s_url in TIER2_SOURCES.items():
            if s_name.lower() in source_name.lower() or s_url in item.get("link", ""):
                is_tier2_source = True
                break
        if is_tier2_source:
            score += 3
        else:
             score += 1

    # Normalize
    # Max: 10 (Type) + 5 (Company) + 5 (Source) = 20
    normalized_score = min(score * 5, 100)
    
    return max(0, normalized_score)

def score_news(news_list):
    """
    Applies scoring to a list of news items.
    Optimized: 
    1. Calculate Rule Score for ALL items.
    2. Filter out 0 scores.
    3. Sort by Rule Score descending.
    4. Take Top 20 candidates.
    5. Calculate AI Score ONLY for Top 20.
    6. Combine scores and re-rank.
    """
    logger.info(f"Scoring {len(news_list)} items")
    
    candidates = []
    for item in news_list:
        rule_score = calculate_rule_score(item)
        
        # Filter out 0 scores (Rejects)
        if rule_score == 0:
            continue
            
        item["rule_score"] = rule_score
        candidates.append(item)
    
    # Sort candidates by rule score descending
    candidates.sort(key=lambda x: x["rule_score"], reverse=True)
    
    # Take top 20 for AI scoring to save API calls/time
    top_candidates = candidates[:20]
    remaining_candidates = candidates[20:]
    
    scored_list = []
    
    # Process top candidates with AI scoring
    for item in top_candidates:
        ai_score = get_ai_score(item)
        item["ai_score"] = ai_score
        # Final Score: Rule * 0.6 + AI * 0.4
        item["final_score"] = item["rule_score"] * 0.6 + ai_score * 0.4
        logger.debug(f"Scored '{item['title'][:30]}...': Rule={item['rule_score']}, AI={ai_score}, Final={item['final_score']}")
        scored_list.append(item)
        
    # Process remaining candidates (without AI score, assume 0 or low)
    for item in remaining_candidates:
        item["ai_score"] = 0
        item["final_score"] = item["rule_score"] * 0.6 # Penalty for not being top tier
        scored_list.append(item)
        
    return scored_list