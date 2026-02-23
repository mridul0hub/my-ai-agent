import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

app = FastAPI()

# Data Structure (Pydantic use karna acchi baat hai, ise barkarar rakha hai)
class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

@app.get("/")
def home():
    return {"status": "Online", "agent": "Professional AI Agent Active"}

@app.post("/webhook")
async def handle_email(email: EmailRequest):
    # API Key check
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "API Key missing in Environment Variables"}
    
    genai.configure(api_key=api_key)
    
    # Model configuration
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 1% Level Prompt: Isse humein structured data milega
    system_prompt = f"""
    You are an expert customer support AI. Analyze the email provided.
    
    STRICT INSTRUCTION: Return ONLY a valid JSON object. Do not include any conversational text before or after the JSON.
    
    EMAIL TO ANALYZE:
    Sender: {email.sender}
    Subject: {email.subject}
    Body: {email.body}
    
    EXPECTED JSON STRUCTURE:
    {{
        "intent": "One word only (Refund, Query, Complaint, or Spam)",
        "summary": "A precise 1-line summary",
        "draft": "A professional, polite reply draft"
    }}
    """
    
    try:
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip()
        
        # CLEANING LOGIC: Agar Gemini markdown code blocks use kare toh usey hatana
        if raw_text.startswith("```"):
            # Pehli line (```json) aur aakhri line (```) ko hatana
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
        
        # String ko Python Dictionary (JSON) mein badalna
        ai_data = json.loads(raw_text)
        
        return {
            "status": "success",
            "data": ai_data  # Ab Make.com ko 'data.intent', 'data.summary' alag milenge
        }
        
    except json.JSONDecodeError:
        return {
            "status": "error", 
            "message": "AI produced invalid JSON format",
            "raw_response": response.text # Debugging ke liye
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}