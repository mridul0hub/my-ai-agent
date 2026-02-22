from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os

app = FastAPI()

# 1. Data Structure
class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

@app.get("/")
def home():
    return {"status": "Online", "agent": "Email Agent Active"}

# 2. Webhook Endpoint (Make.com yahan data bhejega)
@app.post("/webhook")
async def handle_email(email: EmailRequest):
    # Render se API key nikalna
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    # Aapke account ka LATEST model jo aapki list mein tha!
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    system_prompt = f"""
    Analyze this email:
    Sender: {email.sender}
    Subject: {email.subject}
    Body: {email.body}
    
    Task: 
    1. Classify Intent (Refund, Question, Complaint, or Spam)
    2. Write a 1-line Summary
    3. Draft a short, professional reply
    
    Output format:
    Intent: [Text]
    Summary: [Text]
    Reply: [Text]
    """
    
    try:
        response = model.generate_content(system_prompt)
        return {
            "status": "success",
            "ai_analysis": response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}