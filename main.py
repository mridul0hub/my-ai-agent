from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os

app = FastAPI()

# 1. Data Validation Model (Pydantic)
class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

# Gemini Setup (Apni API Key yahan dalein)
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-pro')

@app.get("/")
def home():
    return {"status": "Online", "agent": "Email Triage Agent Ready"}

# 2. Webhook Endpoint
@app.post("/webhook")
async def handle_email(email: EmailRequest):
    print(f"New Email from: {email.sender}") # Ye Render ke logs mein dikhega
    
    # AI ke liye Instructions
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