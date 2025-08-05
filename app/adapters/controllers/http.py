from fastapi import APIRouter, HTTPException
from app.core.domain.models import SendMessagePayload, StatusPayload
from app.core.usecases.send_message import SendMessageUseCase
from app.core.usecases.send_status import SendStatusUseCase
from app.adapters.gateways.meta_api import MetaApiAdapter

router = APIRouter()

@router.post("/send-message")
def send_message(payload: SendMessagePayload):
    try:
        usecase = SendMessageUseCase(MetaApiAdapter())
        result = usecase.execute(payload)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-status")
def send_status(payload: StatusPayload):
    try:
        usecase = SendStatusUseCase(MetaApiAdapter())
        result = usecase.execute(payload)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
