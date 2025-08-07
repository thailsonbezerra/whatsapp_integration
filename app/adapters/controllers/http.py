from fastapi import APIRouter, HTTPException
from app.core.domain.models import SendMessagePayload, StatusPayload
from app.core.usecases.send_message import SendMessageUseCase
from app.core.usecases.send_status import SendStatusUseCase
from app.adapters.gateways import get_meta_adapter

router = APIRouter()

@router.post("/send-message")
def send_message(payload: SendMessagePayload):
    usecase = SendMessageUseCase(get_meta_adapter())
    result = usecase.execute(payload)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send message."))
    return result


@router.post("/send-status")
def send_status(payload: StatusPayload):
    try:
        usecase = SendStatusUseCase(get_meta_adapter())
        result = usecase.execute(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
