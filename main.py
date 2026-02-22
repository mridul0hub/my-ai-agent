from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests
import os

app = FastAPI()

class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

@app.get("/")
def home():
    return {"status": "Online", "agent": "Email Agent Ready"}

@app.post("/webhook")
async def handle_email(email: EmailRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Sabse stable model aur version (v1)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Analyze this email:\nSender: {email.sender}\nSubject: {email.subject}\nBody: {email.body}\n\nTask:\n1. Classify Intent\n2. 1-line Summary\n3. Short Reply\n\nOutput format:\nIntent: [Text]\nSummary: [Text]\nReply: [Text]"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        res_json = response.json()
        
        # Agar error aaye toh poora error return karega
        if 'error' in res_json:
            return {"status": "error", "message": res_json['error']['message']}
            
        ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
        
        return {
            "status": "success",
            "ai_analysis": ai_text
        }
    except Exception as e:
        return {"status": "error", "message": "Connection error to Google AI"}