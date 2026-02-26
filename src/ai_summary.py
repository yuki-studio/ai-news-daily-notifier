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
        return 50

def generate_summary(news_item):
    """
    Generates a structured summary for the news item using AI.
    Returns a dictionary with title, summary, key_points, impact, etc.
    """
    if not client:
        return {
            "title": news_item.get("title"),
            "summary": "AI API Key missing. " + news_item.get("summaries", [""])[0],
            "key_points": ["API Key missing"],
            "impact": "Unknown",
            "publish_date": news_item.get("publish_time").strftime("%Y-%m-%d")
        }
        
    title = news_item.get("title", "")
    summaries = "\n".join(news_item.get("summaries", []))
    sources = ", ".join(news_item.get("sources", []))
    
    prompt = f"""
    Analyze the following AI news and generate a structured summary JSON.
    
    Input News:
    Title: {title}
    Sources: {sources}
    Content Summaries: {summaries}
    
    Requirements:
    1. title: <= 30 words, translated to Chinese if input is English.
    2. summary: 40-60 words, describing company, product, update content. Translated to Chinese.
    3. key_points: 2-3 bullet points, list of capabilities or features. Translated to Chinese.
    4. impact: 30-50 words, describing industry significance. Translated to Chinese.
    5. publish_date: YYYY-MM-DD format.
    
    Output JSON format:
    {{
        "title": "...",
        "summary": "...",
        "key_points": ["...", "..."],
        "impact": "...",
        "publish_date": "YYYY-MM-DD"
    }}
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
        return {
            "title": title,
            "summary": "Failed to generate summary.",
            "key_points": [],
            "impact": "Error",
            "publish_date": str(datetime.now().date())
        }
