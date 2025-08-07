from app.adapters.gateways import get_meta_adapter
from app.adapters.gateways.meta_api import MetaApiAdapter
from fastapi import APIRouter, HTTPException, Response, Request
from config import AppConfig
from app.core.usecases.process_webhook import ProcessWebhookUseCase
from app.adapters.s3.s3_storage_adapter import S3StorageAdapter

router = APIRouter()

@router.get("/webhook", summary="Verificação do Webhook da Meta") 
def verify_webhook(request: Request):
    print("=========================================================")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    print(f"Webhook verification request received: mode={mode}, token={token}, challenge={challenge}")  # Debugging line
    print("=========================================================")

    if mode == "subscribe" and token == AppConfig.VERIFY_TOKEN and challenge:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Falha na verificação do webhook.")

@router.post("/webhook", summary="Recebe notificações da Meta") 
async def handle_webhook(payload: dict):
    print("=========================================================")
    print(f"Webhook payload received: {payload}")
    try:
        usecase = ProcessWebhookUseCase(
            storage=S3StorageAdapter(bucket_name=AppConfig.AWS_BUCKET_NAME),
            meta_api=get_meta_adapter()
        )
        result = usecase.execute(payload["entry"][0]["changes"][0]["value"])
        print(f"Processed webhook result: {result}")
        print("=========================================================")
        return result
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o webhook.")
