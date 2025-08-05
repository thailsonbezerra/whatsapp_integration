from app.core.domain.models import SendMessagePayload
from app.core.ports.input import SendMessageInputPort
from app.core.ports.output import MetaApiOutputPort
from app.utils.mime_types import infer_mime_type_from_url, get_meta_media_type
from typing import Dict

class SendMessageUseCase(SendMessageInputPort):
    def __init__(self, meta_gateway: MetaApiOutputPort):
        self.meta_gateway = meta_gateway

    def execute(self, payload: SendMessagePayload) -> Dict:
        meta_payload = {
            "messaging_product": "whatsapp",
            "to": payload.recipient,
        }

        if payload.type == "text":
            if not payload.body:
                raise ValueError("O campo 'body' é obrigatório para o tipo 'text'.")
            meta_payload["type"] = "text"
            meta_payload["text"] = {"body": payload.body}

        elif payload.type == "media":
            if not payload.body:
                raise ValueError("O campo 'body' (URL) é obrigatório para o tipo 'media'.")
            
            media_mime = infer_mime_type_from_url(payload.body)
            meta_type = get_meta_media_type(media_mime)
            
            if not meta_type:
                raise ValueError("Tipo de mídia não suportado.")
            
            meta_payload["type"] = meta_type
            media_content = {"link": payload.body}
            if payload.subject:
                media_content["caption"] = payload.subject
            meta_payload[meta_type] = media_content

        elif payload.type == "reaction":
            if not payload.body or not payload.origin_msg_id:
                raise ValueError("Campos 'body' e 'origin_msg_id' são obrigatórios para reações.")
            meta_payload["type"] = "reaction"
            meta_payload["reaction"] = {
                "message_id": payload.origin_msg_id,
                "emoji": payload.body
            }

        if payload.origin_msg_id and payload.type != "reaction":
            meta_payload["context"] = {"message_id": payload.origin_msg_id}

        return self.meta_gateway.send_message(meta_payload)
