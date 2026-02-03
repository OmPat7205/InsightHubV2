import os
import json
from groq import Groq
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load for local dev
from dotenv import load_dotenv, find_dotenv

# Load for local dev
load_dotenv(find_dotenv())

# Initialize Groq
# Prioritize GROQ_API_KEY, fallback to env var for local dev
api_key = os.getenv("GROQ_API_KEY")
client = None

if api_key:
    client = Groq(api_key=api_key)

def analyze_sector(sector, items: List[Dict]) -> Dict[str, Any]:
    """
    Sends the top articles to Groq (Llama 3) for analysis.
    Returns a structured dictionary with execution summary, risk level, action cards, etc.
    """
    if not client:
        print("WARNING: GROQ_API_KEY not found. Returning dummy data.")
        return _dummy_response(sector)

    # Prepare context for the LLM
    articles_text = ""
    for idx, item in enumerate(items[:15]):  # Can execute more items with Groq
        title = item.get("title", "No Title")
        summary = item.get("summary", "No Summary")
        articles_text += f"Article {idx+1}:\nTitle: {title}\nSummary: {summary}\n\n"

    system_prompt = f"""
    You are an Expert Intelligence Analyst for the {sector.name}.
    Audience: {sector.audience}.
    
    Goal: Produce a Daily Intelligence Brief JSON.
    
    Structure:
    {{
        "executive_summary": ["Bullet 1", "Bullet 2", "Bullet 3"],
        "risk_level": "RED (High) | YELLOW (Moderate) | GREEN (Low)",
        "action_cards": [
            {{
                "title": "Short Title",
                "severity": "High/Medium/Low",
                "implication": "Business impact",
                "next_steps": {{
                    "Role1": ["Step 1"],
                    "Role2": ["Step 1"]
                }}
            }}
        ],
        "forward_looking_signals": ["Signal 1", "Signal 2"]
    }}
    
    Roles to use in next_steps: {', '.join(sector.roles)}
    Output JSON ONLY. No markdown.
    """

    user_prompt = f"Analyze these articles:\n{articles_text}"

    try:
        completion = client.chat.completions.create(
            # Using Llama 3.3 70B (Current Groq Production Model)
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        text = completion.choices[0].message.content
        return json.loads(text)

    except Exception as e:
        print(f"Error calling Groq: {e}")
        return _dummy_response(sector)

def _dummy_response(sector) -> Dict[str, Any]:
    """Fallback if no API key or error"""
    return {
        "executive_summary": ["No API Key provided.", "Please set GROQ_API_KEY.", "Using fallback mode."],
        "risk_level": "GREEN (Low)",
        "action_cards": [],
        "forward_looking_signals": ["Configure API key to see signals."]
    }
