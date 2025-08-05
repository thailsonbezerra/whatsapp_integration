from fastapi import APIRouter, Request, HTTPException, Response
from app.adapters.mappers.webhook_normalizer import normalize_webhook_event
from config import AppConfig

router = APIRouter()

@router.get("/webhook", summary="Verificação do Webhook da Meta") 
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == AppConfig.VERIFY_TOKEN and challenge:
        print("Webhook verificado com sucesso!")
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Falha na verificação do webhook.")

@router.post("/webhook", summary="Recebe notificações da Meta") 
async def handle_webhook(payload: dict):
    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        phone_number_waba = value.get("metadata", {}).get("phone_number_id")

        data = normalize_webhook_event(value, phone_number_waba)

        return data
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o webhook.")