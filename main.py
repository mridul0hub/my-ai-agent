from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# FastAPI ka instance banao
app = FastAPI()

# Data ka structure define karo (Pydantic ki madad se)
class WebhookPayload(BaseModel):
    user_name: str
    message: str
    priority: Optional[int] = 1

# 1. GET Root: Check karne ke liye ki server zinda hai
@app.get("/")
def home():
    return {"message": "Bhai, AI Factory Live Hai!", "status": "Running"}

# 2. POST Webhook: Jahan data receive hoga
@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    print(f"Data Aaya! Name: {payload.user_name}, Msg: {payload.message}")
    
    # Yahan hum logic likh sakte hain (jaise Gemini ko call karna)
    response_msg = f"Hello {payload.user_name}, humein aapka message mil gaya!"
    
    return {
        "status": "success",
        "ai_response": response_msg,
        "received_data": payload
    }