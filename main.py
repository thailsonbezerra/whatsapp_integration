from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WABA_PHONE_ID = os.getenv("WABA_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_API_URL = os.getenv("META_API_URL", "https://graph.facebook.com/v22.0")

# falhar cedo se faltar configuração essencial
missing = [k for k, v in {
    "ACCESS_TOKEN": ACCESS_TOKEN,
    "WABA_PHONE_ID": WABA_PHONE_ID,
    "VERIFY_TOKEN": VERIFY_TOKEN
}.items() if not v]
if missing:
    raise RuntimeError(f"Faltando variáveis de ambiente obrigatórias: {', '.join(missing)}")

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

@app.get("/webhook", summary="Verificação do Webhook da Meta", response_model=None)
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge is not None:
        print("Webhook verificado com sucesso!")
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Falha na verificação do webhook.")

@app.post("/webhook", summary="Recebe as notificações de status da Meta")
async def handle_webhook(payload: Dict[str, Any]):
    # Em produção: validar assinatura X-Hub-Signature-256 aqui.
    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        if "statuses" in value:
            status_data = value["statuses"][0]
            wamid = status_data["id"]
            status = status_data["status"]
            timestamp = status_data["timestamp"]
            
            # --- DEBUG ---
            error_details = None
            if "errors" in status_data:
                error_details = status_data["errors"][0]
                error_code = error_details.get("code")
                error_title = error_details.get("title")
                error_message = error_details.get("message")
                
                print(f"--- ERRO RECEBIDO ---")
                print(f"WAMID: {wamid}")
                print(f"Status: {status}")
                print(f"Código do Erro: {error_code}")
                print(f"Título: {error_title}")
                print(f"Mensagem: {error_message}")
                print(f"--- FIM DO ERRO ---")
            else:
                print(f"Status recebido: {status} para WAMID: {wamid} em {timestamp}")

        return {"success": True}
        
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o webhook.")