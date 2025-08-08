from fastapi import APIRouter
from fastapi.responses import JSONResponse
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
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": result.get("error", "Failed to send message.")
            }
        )
    
    return result


@router.post("/send-status")
def send_status(payload: StatusPayload):
    usecase = SendStatusUseCase(get_meta_adapter())
    result = usecase.execute(payload)

    if not result.get("success"):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": result.get("error", "Failed to send status.")
            }
        )

    return {
        "success": True,
    }
