import requests
import json
from src.config import FEISHU_WEBHOOK
from src.utils import setup_logger

from datetime import datetime

logger = setup_logger("feishu_sender")

def send_to_feishu(summaries):
    """
    Sends the list of summarized news to Feishu via Webhook.
    """
    if not FEISHU_WEBHOOK:
        logger.warning("FEISHU_WEBHOOK not set. Skipping notification.")
        return

    logger.info(f"Sending {len(summaries)} items to Feishu")
    
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Header
    card_header = {
        "title": {
            "tag": "plain_text",
            "content": f"🤖 AI行业快讯 | {current_date}"
        },
        "template": "blue"
    }
    
    elements = []
    
    for i, item in enumerate(summaries):
        # Separator for items after the first one
        if i > 0:
            elements.append({"tag": "hr"})
            
        # Title with Emoji number
        emoji_num = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i] if i < 5 else f"{i+1}."
        
        # Ensure we have a valid URL. 
        url = item.get('url')
        if not url or url == "":
            links = item.get('links', [])
            if links:
                url = links[0]
            else:
                url = "#"

        source_name = item.get('source_name', 'Unknown Source')

        # Combined Text Block
        # PRD v1.5 Requirements:
        # 1. Title
        # 2. Event Summary
        # 3. Key Changes (Bulleted list)
        # 4. Source Link
        # 5. Publish Time
        
        publish_date = item.get('publish_date', current_date)
        if 'UTC+8' not in publish_date:
             publish_date += " UTC+8"
        
        # Format Key Changes
        key_changes_list = item.get('key_changes', [])
        key_changes_text = ""
        if key_changes_list:
            key_changes_text = "\n**关键变化点：**\n" + "\n".join([f"- {change}" for change in key_changes_list])
        
        # NOTE: Using a single Lark Markdown block for better formatting
        content = f"**{emoji_num} {item['title']}**\n\n{item['summary']}{key_changes_text}\n\n来源：[{source_name}]({url})\n发布时间：{publish_date}"

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })

    card = {
        "msg_type": "interactive",
        "card": {
            "header": card_header,
            "elements": elements
        }
    }
    
    try:
        response = requests.post(
            FEISHU_WEBHOOK, 
            headers={"Content-Type": "application/json"},
            data=json.dumps(card)
        )
        response.raise_for_status()
        
        # Check for Feishu specific error codes in body even if HTTP 200
        res_json = response.json()
        if res_json.get("code") and res_json.get("code") != 0:
            logger.error(f"Feishu API Error: {res_json}")
        else:
            logger.info("Successfully sent to Feishu")
            
    except Exception as e:
        logger.error(f"Failed to send to Feishu: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"Feishu Response: {e.response.text}")

if __name__ == "__main__":
    # Test
    # UPDATED MOCK DATA (2026-02-27 REALISTIC SCENARIOS)
    # Replaced outdated news with 2026-consistent mock events based on industry trajectory
    mock_news = [
        {
            "title": "OpenAI发布Sora v2.0",
            "summary": "OpenAI正式发布视频生成模型Sora v2.0，支持生成长达2分钟的4K 60fps视频，并新增音效自动同步功能。",
            "key_changes": [
                "视频时长上限提升至2分钟",
                "原生支持音效生成与同步",
                "API面向Plus用户开放公测"
            ],
            "url": "https://openai.com/index/sora/",
            "source_name": "OpenAI News",
            "publish_date": "2026-02-26 21:10"
        },
        {
             "title": "GitHub Copilot Workspace 2.0发布",
             "summary": "GitHub发布Copilot Workspace 2.0，引入了全新的'Agent Mode'，可自主完成从Issue到PR的完整修复流程。",
             "key_changes": [
                 "新增全自动Agent模式",
                 "支持跨仓库上下文理解",
                 "移动端App同步上线"
             ],
             "url": "https://github.blog/2026-02-27-introducing-copilot-workspace-2/", # Mock URL
             "source_name": "The GitHub Blog",
             "publish_date": "2026-02-27 07:15"
        },
        {
            "title": "DeepSeek R1模型正式开源",
            "summary": "DeepSeek发布并开源新一代推理模型DeepSeek R1，在数学和代码任务上表现出卓越性能。",
            "key_changes": [
                "基于FP8混合精度训练",
                "开源权重DeepSeek-R1-Lite-Preview",
                "API已同步上线"
            ],
            "url": "https://api-docs.deepseek.com/news/news0125",
            "source_name": "DeepSeek News",
            "publish_date": "2026-01-20 10:00"
        },
        {
            "title": "Google发布Gemini 3.1 Pro",
            "summary": "Google推出Gemini 3.1 Pro模型，专为处理高度复杂的推理任务而设计，并在全球Gemini应用中上线。",
            "key_changes": [
                "针对复杂逻辑推理优化",
                "Google AI Pro/Ultra用户可用",
                "支持更长上下文与多模态输入"
            ],
            "url": "https://gemini.google/release-notes/",
            "source_name": "Gemini Release Notes",
            "publish_date": "2026-02-27 06:45"
        },
        {
            "title": "AWS Bedrock支持Claude 3.5 Opus",
            "summary": "AWS宣布Amazon Bedrock正式支持Anthropic最强模型Claude 3.5 Opus，为企业级高负载任务提供更强算力支持。",
            "key_changes": [
                "Claude 3.5 Opus正式上架",
                "支持预配置吞吐量模式",
                "符合HIPAA合规标准"
            ],
            "url": "https://aws.amazon.com/blogs/aws/claude-3-5-opus-now-available-on-amazon-bedrock/", # Mock URL
            "source_name": "AWS News Blog",
            "publish_date": "2026-02-27 05:20"
        }
    ]
    send_to_feishu(mock_news)