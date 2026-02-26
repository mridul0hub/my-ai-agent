import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

app = FastAPI()

class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

@app.get("/")
def home():
    return {"status": "Online", "agent": "Elite AI Support Executive Active"}

@app.post("/webhook")
async def handle_email(email: EmailRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "API Key missing in Environment Variables"}
    
    genai.configure(api_key=api_key)
    
    # Using Gemini 1.5/2.0 Flash for maximum speed/efficiency
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # BILLIONAIRE LEVEL PROMPT: Focus on CX (Customer Experience) & Precision
    system_prompt = f"""
    You are a world-class Customer Success Executive for a premium brand. Your goal is to maximize customer retention and handle issues with elite precision.

    STRICT INSTRUCTIONS:
    1. CONTEXTUAL INTELLIGENCE: Do NOT ask for information already mentioned in the email (e.g., Order IDs, names, specific complaints). Acknowledge them directly.
    2. URGENCY ANALYSIS: Classify the email as 'High', 'Medium', or 'Low'.
       - 'High': Angry tone, legal threats, refund demands, or damaged product.
       - 'Medium': General technical queries or order status updates.
       - 'Low': Feedback or generic greetings.
    3. TONE: Professional, empathetic, and concise.

    EMAIL TO ANALYZE:
    Sender: {email.sender}
    Subject: {email.subject}
    Body: {email.body}

    OUTPUT: Return ONLY a valid JSON object.
    
    EXPECTED JSON STRUCTURE:
    {{
        "intent": "Short category (Refund, Complaint, Query, etc.)",
        "urgency": "High/Medium/Low",
        "summary": "A precise 1-line summary showing you understood the specific issue",
        "draft": "A personalized, ready-to-send professional reply"
    }}
    """
    
    try:
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip()
        
        # CLEANING LOGIC (Robust for Markdown)
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
        
        ai_data = json.loads(raw_text)
        
        return {
            "status": "success",
            "data": ai_data
        }
        
    except json.JSONDecodeError:
        return {"status": "error", "message": "AI failed to produce valid JSON", "raw": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}