from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

load_dotenv() 

app = FastAPI()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WABA_PHONE_ID = os.getenv("WABA_PHONE_ID")
META_API_URL = os.getenv("META_API_URL", "https://graph.facebook.com/v22.0")

class MessagePayload(BaseModel):
    sender: str
    recipient: str
    message_type: str
    content: str
    message_id: str = None 

@app.post("/send-message", summary="Envia uma mensagem SAC para o WhatsApp")
def send_message(payload: MessagePayload):
    print("Authorization token:", ACCESS_TOKEN)
    meta_payload = {
        "messaging_product": "whatsapp",
        "to": payload.recipient,
        "type": payload.message_type,
        "text": {"body": payload.content}
    }
    
    if payload.message_id:
        meta_payload["context"] = {"message_id": payload.message_id}

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{META_API_URL}/{WABA_PHONE_ID}/messages"
    
    try:
        response = requests.post(url, headers=headers, json=meta_payload)
        response.raise_for_status() 
        
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=response.status_code, detail=f"Erro da API da Meta: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
