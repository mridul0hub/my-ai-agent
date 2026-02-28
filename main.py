import os
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from supabase import create_client, Client

app = FastAPI()

# --- 1. CONFIGURATION (Environment Variables) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Jo URL aapne Notepad mein save kiya
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Jo Secret Key (Service Role) aapne save ki

# Supabase Client Initialize karo
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

class EmailRequest(BaseModel):
    sender: str
    subject: Optional[str] = "No Subject"
    body: str

@app.get("/")
def home():
    return {"status": "Online", "platform": "Mridul AI SaaS Engine v1.0"}

# --- 2. THE SAAS WEBHOOK (Dynamic Client Handling) ---
@app.post("/webhook/{client_id}")
async def handle_saas_email(client_id: int, email: EmailRequest):
    try:
        # STEP A: Supabase se Client ki details nikalo
        # Hum check kar rahe hain ki kya ye client ID database mein hai?
        response = supabase.table("clients").select("*").eq("id", client_id).single().execute()
        client_data = response.data

        if not client_data:
            raise HTTPException(status_code=404, detail="Client not found in our system")
        
        # Subscription Check
        if not client_data.get('is_active', False):
            return {"status": "error", "message": "Subscription inactive. Please pay."}

        # STEP B: Billionaire Brain Logic with Anti-Scam Guardrails
        knowledge_base = client_data.get('knowledge_base', 'General Assistant')
        business_name = client_data.get('business_name', 'Our Business')
        ai_tone = client_data.get('ai_tone', 'Professional')

        system_prompt = f"""
        You are an Elite AI Agent for '{business_name}'. 
        
        BUSINESS RULES & KNOWLEDGE:
        {knowledge_base}
        
        TONE: {ai_tone}

        STRICT TASK:
        1. SCAM DETECTION: If the email contains suspicious links, OTP requests, or phishing language, mark 'is_scam' as true.
        2. ACCURACY: Only answer from the Knowledge Base. If unsure, say 'I will forward this to a human expert'.
        3. CONFIDENCE: Give a score from 0-100 on how sure you are about the reply.

        CUSTOMER EMAIL:
        From: {email.sender} | Sub: {email.subject}
        Body: {email.body}

        OUTPUT FORMAT (JSON ONLY):
        {{
            "is_scam": boolean,
            "confidence_score": number,
            "intent": "category",
            "summary": "1-line summary",
            "reply_draft": "Your professional response"
        }}
        """

        # STEP C: AI Generation
        ai_response = model.generate_content(system_prompt)
        raw_text = ai_response.text.strip()

        # Markdown Cleaning
        if raw_text.startswith("```"):
            raw_text = raw_text.splitlines()[1:-1]
            raw_text = "\n".join(raw_text).strip()

        processed_data = json.loads(raw_text)

        # STEP D: Log the Interaction (Optional: Save to a 'logs' table in Supabase)
        # Isse client ko unke dashboard par dikhega ki AI ne kya jawab diya.

        return {
            "status": "success",
            "client": business_name,
            "ai_analysis": processed_data
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}