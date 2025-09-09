from app.adapters.gateways import get_meta_adapter
from app.adapters.gateways.meta_api import MetaApiAdapter
from fastapi import APIRouter, HTTPException, Response, Request
from config import AppConfig
from app.core.usecases.process_webhook import ProcessWebhookUseCase
from app.adapters.s3.s3_storage_adapter import S3StorageAdapter
import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.get("/webhook", summary="Verificação do Webhook da Meta") 
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == AppConfig.VERIFY_TOKEN and challenge:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Falha na verificação do webhook.")

@router.post("/webhook", summary="Recebe notificações da Meta") 
async def handle_webhook(payload: dict):
    try:
        usecase = ProcessWebhookUseCase(
            storage=S3StorageAdapter(bucket_name=AppConfig.AWS_BUCKET_NAME),
            meta_api=get_meta_adapter()
        )

        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(payload)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        result = usecase.execute(
            payload["entry"][0]["id"],
            payload["entry"][0]["changes"][0]["value"]
        )
        
        return result
    except Exception as e:
        logging.error(f"Erro ao processar webhook file: webhook.py: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o webhook.")
