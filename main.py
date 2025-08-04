from typing import Any, Dict, Optional, Literal
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

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

class SendMessagePayload(BaseModel):
    recipient: str
    sender: str
    type: Literal["text", "media", "reaction"]
    body: Optional[str] = None
    subject: Optional[str] = None
    origin_msg_id: Optional[str] = None
    

class StatusPayload(BaseModel):
    type: Literal["read", "writing"]
    msg_id: str
    sender: str

@app.post("/send-message", summary="Envia uma mensagem para o WhatsApp")
def send_message(payload: SendMessagePayload):
    """
    Endpoint que usa o payload unificado para enviar mensagens de texto, mídia e reações.
    """
    try:
        # Com o sender (número do waba) pegar o waba_phone_id no db
        meta_payload = encode_to_meta_api(payload)
        
        return meta_payload            
       
        # Integrar com a API da Meta
        # Descomente as linhas abaixo para enviar a mensagem via API da Meta
        
        # headers = {
        #     "Authorization": f"Bearer {ACCESS_TOKEN}",
        #     "Content-Type": "application/json"
        # }
        # url = f"{META_API_URL}/{WABA_PHONE_ID}/messages"
        
        # response = requests.post(url, headers=headers, json=meta_payload)
        # response.raise_for_status() 
        
        # return {"success": True, "data": response.json()}
    
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=response.status_code, detail=f"Erro da API da Meta: {err.response.text}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@app.post("/send-status", summary="Envia indicação de read/typing para o WhatsApp")
def send_status(payload: StatusPayload):
    """
    type: 'read' ou 'writing'
    msg_id: id da mensagem de referência
    sender: número do waba
    """
    try:
        meta_payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "message_id": payload.msg_id,
            "status": "read",
        }


        if payload.type == "writing":
            meta_payload["typing_indicator"] = {"type": "text"}

        # enviar para a API da Meta
        # com o sender (número do waba) pegar o waba_phone_id no db

        # headers = {
        #     "Authorization": f"Bearer {ACCESS_TOKEN}",
        #     "Content-Type": "application/json",
        # }
        # url = f"{META_API_URL}/{WABA_PHONE_ID}/messages"

        # response = requests.post(url, headers=headers, json=meta_payload)
        # response.raise_for_status()

        # return {"success": True, "data": response.json()}

        return meta_payload
    
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code if err.response is not None else 500
        detail = err.response.text if err.response is not None else str(err)
        raise HTTPException(status_code=status_code, detail=f"Erro da API da Meta: {detail}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
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
        
        phone_number_waba = value.get("metadata", {}).get("phone_number_id")
        

        print(f"Payload recebido: {payload}")
        data = normalize_webhook_event(value, phone_number_waba)

        return {"success": True, "data": data}

    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o webhook.")
    
from typing import Any, Dict, Optional

def normalize_webhook_event(payload: Dict[str, Any], phone_number_waba: str) -> Optional[Dict[str, Any]]:
    unified = {
        "recipient": None,
        "sender": phone_number_waba,
        "message_id": None,
        "timestamp": None,
        "subject": None,
        "body": None,
        "type": None,
        "event_type": None,
        "channel_type": "whatsapp",
        "origin_msg_id": None,
    }

    print(payload)
    
    # --------------------
    # Processa eventos de ERROS
    # --------------------
    if "errors" in payload:
        try:
            error_data = payload["errors"][0]
            # TODO: Fazer o mapeamento dos códigos de erro da Meta para os códigos de erro do sistema
            code_error_meta = error_data.get("code")
            unified["event_type"] = "error"
            unified["timestamp"] = payload.get("timestamp")
            unified["subject"] = error_data.get("title")
            unified["body"] = error_data.get("message")
            unified["type"] = "failed" # Um erro é um tipo de falha
            unified["message_id"] = payload.get("id")
            unified["recipient"] = payload.get("from")
            return unified
        except Exception:
            return None
    
    # status event
    elif "statuses" in payload:
        try:
            status_data = payload["statuses"][0]
            unified["event_type"] = "status"
            unified["message_id"] = status_data.get("id")
            unified["timestamp"] = status_data.get("timestamp")
            unified["recipient"] = status_data.get("recipient_id")
            unified["type"] = status_data.get("status")  # sent, delivered etc.
            # body/subject ficam vazios para status
            return unified
        except Exception:
            return None

    # message event
    elif "messages" in payload:
            try:
                message_data = payload["messages"][0]
                unified["event_type"] = "message"
                unified["message_id"] = message_data.get("id")
                unified["timestamp"] = message_data.get("timestamp")
                unified["recipient"] = message_data.get("from")
                
                msg_type = message_data.get("type")

                # Captura a mensagem contextual (reply)
                context = message_data.get("context", {})
                if context:
                    unified["origin_msg_id"] = context.get("id")

                if msg_type == "text":
                    unified["type"] = "text"
                    unified["body"] = message_data.get("text", {}).get("body")
                
                elif msg_type in ["image", "video", "audio", "document", "sticker"]:
                    media_data = message_data.get(msg_type, {})
                    unified["type"] = "media"
                    unified["subject"] = media_data.get("caption") # Legenda como subject
                    unified["body"] = media_data.get("id") # ID da mídia como body
                
                elif msg_type == "button":
                    button_data = message_data.get("button", {})
                    unified["type"] = "interactive_reply"
                    unified["subject"] = button_data.get("text") # Título como subject
                    unified["body"] = button_data.get("payload") # Payload/ID do botão como body
                
                # elif msg_type == "interactive":
                #     interactive_data = message_data.get("interactive", {})
                #     interactive_type = interactive_data.get("type")
                #     unified["type"] = "interactive_reply"
                #     if interactive_type == "list_reply":
                #         reply_data = interactive_data.get("list_reply", {})
                #         unified["subject"] = reply_data.get("title")
                #         unified["body"] = reply_data.get("id")
                #     elif interactive_type == "button_reply":
                #         reply_data = interactive_data.get("button_reply", {})
                #         unified["subject"] = reply_data.get("title")
                #         unified["body"] = reply_data.get("id")
                
                elif msg_type == "reaction":
                    reaction_data = message_data.get("reaction", {})
                    unified["type"] = "reaction"
                    unified["body"] = reaction_data.get("emoji")
                    unified["origin_msg_id"] = reaction_data.get("message_id") # ID da mensagem reagida
                    
                return unified
            except Exception as e:
                print(f"Erro ao processar mensagem do webhook: {e}")
                return None
            
    return None

def infer_mime_type_from_url(url: str) -> str:
    """
    Inferir o mime-type de uma URL com base na extensão do arquivo.
    """
    # Mapeamento de extensões para mime-types
    mime_types = {
        # Audio
        ".aac": "audio/aac",
        ".amr": "audio/amr",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        
        # Documentos
        ".txt": "text/plain",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
        
        # Imagens
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg", 
        ".png": "image/png",

        # Vídeos
        ".3gp": "video/3gpp",
        ".mp4": "video/mp4",
    }
    
    # Extrai o caminho do arquivo da URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Extrai a extensão
    extension = os.path.splitext(path)[1].lower()
    
    return mime_types.get(extension)

def encode_to_meta_api(payload: SendMessagePayload) -> Dict[str, Any]:
    """
    Transforma o payload unificado no formato da API da Meta.
    """
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
        
        meta_media_type = infer_mime_type_from_url(payload.body)
        if not meta_media_type:
            raise ValueError("Não foi possível inferir o tipo de mídia da URL fornecida.")
        
        if meta_media_type.startswith("image/"):
            meta_media_type = "image"
        elif meta_media_type.startswith("video/"):  
            meta_media_type = "video"
        elif meta_media_type.startswith("audio/"):
            meta_media_type = "audio"
        elif meta_media_type in ["application/pdf", "application/msword",
                                 "application/vnd.ms-excel",
                                 "application/vnd.ms-powerpoint",
                                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                 "text/plain"]:
            meta_media_type = "document"
        else:
            raise ValueError(f"Tipo de mídia não suportado: {meta_media_type}")
        
        meta_payload["type"] = meta_media_type
        
        media_content = {"link": payload.body}
        if payload.subject:
            media_content["caption"] = payload.subject
        
        meta_payload[meta_media_type] = media_content

    elif payload.type == "reaction":
        if not payload.body or not payload.origin_msg_id:
            raise ValueError("Os campos 'body' (emoji) e 'origin_msg_id' são obrigatórios para 'reaction'.")
        meta_payload["type"] = "reaction"
        meta_payload["reaction"] = {
            "message_id": payload.origin_msg_id,
            "emoji": payload.body
        }
    
    if payload.origin_msg_id and payload.type != "reaction":
        meta_payload["context"] = {"message_id": payload.origin_msg_id}

    return meta_payload   
