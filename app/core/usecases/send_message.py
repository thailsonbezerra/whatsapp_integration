from app.core.domain.models import SendMessagePayload
from app.core.ports.input import SendMessageInputPort
from app.core.ports.output import MetaApiOutputPort
from app.utils.mime_types import infer_mime_type_from_url, get_meta_media_type
from typing import Dict

class SendMessageUseCase(SendMessageInputPort):
    def __init__(self, meta_gateway: MetaApiOutputPort):
        self.meta_gateway = meta_gateway

    def execute(self, payload: SendMessagePayload) -> Dict:
        validation_error = self._validate_payload(payload)
        if validation_error:
            return {"success": False, "error": validation_error}

        meta_payload = self._build_meta_payload(payload)

        result = self.meta_gateway.send_message(meta_payload)
        if "error" in result:
            return {"success": False, "error": "Failed to send message to Meta API."}

        return {"success": True, "data": result}

    def _validate_payload(self, payload: SendMessagePayload) -> str | None:
        if payload.type == "text" and not payload.body:
            return "O campo 'body' é obrigatório para o tipo 'text'."

        if payload.type == "media":
            if not payload.body:
                return "O campo 'body' (URL) é obrigatório para o tipo 'media'."
            media_mime = infer_mime_type_from_url(payload.body)
            meta_type = get_meta_media_type(media_mime)
            if not meta_type:
                return "Tipo de mídia não suportado."

        if payload.type == "reaction":
            if not payload.body or not payload.origin_msg_id:
                return "Campos 'body' e 'origin_msg_id' são obrigatórios para reações."

        return None

    def _build_meta_payload(self, payload: SendMessagePayload) -> Dict:
        meta_payload = {
            "messaging_product": "whatsapp",
            "to": payload.recipient,
        }

        if payload.type == "text":
            meta_payload["type"] = "text"
            meta_payload["text"] = {"body": payload.body}

        elif payload.type == "notification":
            meta_payload["type"] = "template"
            
            # Constrói o dicionário de componentes para o template
            template_components = []
            if payload.body:  # Verifica se a lista de parâmetros não está vazia
                parameters = [{"type": "text", "text": param} for param in payload.body]
                template_components.append({
                    "type": "body",
                    "parameters": parameters
                })

            meta_payload["template"] = {
                "name": payload.subject,
                "language": {
                    "code": "pt_BR"
                },
                "components": template_components
            }
            
        elif payload.type == "media":
            media_mime = infer_mime_type_from_url(payload.body)
            meta_type = get_meta_media_type(media_mime)
            meta_payload["type"] = meta_type
            media_content = {"link": payload.body}
            if payload.subject:
                media_content["caption"] = payload.subject
            meta_payload[meta_type] = media_content

        elif payload.type == "reaction":
            meta_payload["type"] = "reaction"
            meta_payload["reaction"] = {
                "message_id": payload.origin_msg_id,
                "emoji": payload.body
            }

        if payload.origin_msg_id and payload.type != "reaction":
            meta_payload["context"] = {"message_id": payload.origin_msg_id}

        return meta_payload
