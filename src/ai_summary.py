import json
import os
from openai import OpenAI
from src.config import AI_API_KEY, AI_MODEL, AI_PROVIDER, AI_BASE_URL
from src.utils import setup_logger

logger = setup_logger("ai_summary")

client = None
if AI_API_KEY:
    if AI_BASE_URL:
        client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
    elif AI_PROVIDER == "deepseek":
        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
    else:
        client = OpenAI(api_key=AI_API_KEY)
else:
    logger.warning("AI_API_KEY not set. AI features will be disabled or mocked.")

def get_ai_score(news_item):
    """
    Asks AI to score the importance of the news item (0-100).
    """
    if not client:
        return 50 # Default if no API key
        
    title = news_item.get("title", "")
    summary = " ".join(news_item.get("summaries", []))[:1000] # Truncate to save tokens
    
    prompt = f"""
    Give this AI news item an importance score (0-100).
    Consider: Industry Impact, Technical Breakthrough, Company Influence.
    Return ONLY the number.
    
    Title: {title}
    Summary: {summary}
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI news analyst. Output only a number between 0 and 100."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        content = response.choices[0].message.content.strip()
        # Extract number
        import re
        match = re.search(r'\d+', content)
        if match:
            return int(match.group())
        return 50
    except Exception as e:
        logger.error(f"Error getting AI score: {e}")
        # Log response body if available for debugging
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"API Response: {e.response.text}")
        return 50

def generate_summary(news_item):
    """
    Generates a structured summary for the news item using AI.
    Returns a dictionary with title, summary, key_changes, etc.
    """
    if not client:
        # Fallback to RSS summary if available
        fallback_summary = news_item.get("summaries", ["No summary available."])[0]
        # Clean up HTML tags if simple
        import re
        fallback_summary = re.sub('<[^<]+?>', '', fallback_summary)[:200] + "..."
        
        return {
            "title": news_item.get("title", "No Title"),
            "summary": f"[AI Key Missing] {fallback_summary}",
            "key_changes": ["Configure AI_API_KEY to enable smart summaries"],
            "source_name": news_item.get("source", "RSS Source"),
            "url": news_item.get("link", "#")
        }
        
    title = news_item.get("title", "")
    summaries = "\n".join(news_item.get("summaries", []))
    sources = ", ".join(news_item.get("sources", []))
    
    prompt = f"""
    You are an AI News Feed Editor. 
    Your task is to extract high-value information from the input news for Product Managers and Developers.
    
    Input News:
    Title: {title}
    Sources: {sources}
    Content Summaries: {summaries}

    Output JSON Format:
    {{
        "title": "Chinese Title",
        "summary": "Chinese Summary",
        "key_changes": ["Change 1", "Change 2", "Change 3"],
        "source_name": "Source Name",
        "url": "Original URL"
    }}
    
    CRITICAL REQUIREMENTS (PRD v1.5):
    
    1. Title:
       - Format: [Company/Product] + [Action/Event]
       - No "Marketing Fluff" (e.g. Revolution, Game Changer).
       - Keep it factual. 
       
    2. Summary:
       - 1 paragraph, objective, factual.
       - Focus on WHAT happened.
    
    3. Key Changes (CRITICAL):
       - List specific changes (Bullet points).
       - Must include at least one of: New Model Name, API Change, Price Change, Parameter Change, New Feature Name.
       - If no specific change is found, return empty list (which will cause rejection).
       
    4. Language:
       - Simplified Chinese.
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI news assistant. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"API Response: {e.response.text}")
        return {
            "title": title,
            "summary": "Failed to generate summary.",
            "key_changes": [],
            "source_name": "Unknown",
            "url": ""
        }