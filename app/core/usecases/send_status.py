from typing import Dict
from app.core.domain.models import StatusPayload
from app.core.ports.input import SendStatusInputPort
from app.core.ports.output import MetaApiOutputPort

class SendStatusUseCase(SendStatusInputPort):
    def __init__(self, meta_gateway: MetaApiOutputPort):
        self.meta_gateway = meta_gateway

    def execute(self, payload: StatusPayload) -> Dict:
        meta_payload: Dict = {
            "messaging_product": "whatsapp",
            "message_id": payload.msg_id,
            "status": "read"
        }

        if payload.type == "writing":
            meta_payload["typing_indicator"] = {"type": "text"}

        result = self.meta_gateway.send_message(meta_payload)
        if "error" in result:
            return {"success": False, "error": "Failed to send status to Meta API."}
        
        return {"success": True, "data": result}
