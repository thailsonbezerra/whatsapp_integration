from typing import Dict, Optional

def normalize_webhook_event(payload: Dict, phone_number_waba: str) -> Optional[Dict]:
    unified = {
        "recipient": None,
        "sender_name": None,
        "sender": None,
        "message_id": None,
        "timestamp": None,
        "subject": None,
        "body": None,
        "type": None,
        "event_type": None,
        "channel_type": "whatsapp",
        "origin_msg_id": None,
    }

    if "errors" in payload:
        return _normalize_error_event(payload, unified)
    elif "statuses" in payload:
        return _normalize_status_event(payload, unified, phone_number_waba)
    elif "messages" in payload:
        return _normalize_message_event(payload, unified, phone_number_waba)

    return None

def _normalize_error_event(payload, unified):
    try:
        error = payload["errors"][0]
        unified.update({
            "event_type": "error",
            "timestamp": payload.get("timestamp"),
            "subject": error.get("title"),
            "body": error.get("message"),
            "type": "failed",
            "message_id": payload.get("id"),
            "sender": payload.get("from")
        })
        return unified
    except Exception:
        return None

def _normalize_status_event(payload, unified, phone_number_waba):
    print("Normalizing status event...")
    try:
        status = payload["statuses"][0]
        unified.update({
            "event_type": "status",
            "message_id": status.get("id"),
            "timestamp": status.get("timestamp"),
            "sender": phone_number_waba,
            "recipient": status.get("recipient_id"),
            "type": status.get("status"),
        })
        return unified
    except Exception:
        return None

def _normalize_message_event(payload, unified, phone_number_waba):
    print("Normalizing message event...")
    try:
        contact = payload["contacts"][0]
        profile = contact.get("profile", {})
        
        message = payload["messages"][0]
        msg_type = message.get("type")
        context = message.get("context", {})

        unified.update({
            "event_type": "message",
            "message_id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "sender": message.get("from"),
            "sender_name": profile.get("name"),
            "recipient": phone_number_waba,
            "origin_msg_id": context.get("id") if context else None,
            "type": msg_type
        })

        if msg_type == "text":
            unified["body"] = message.get("text", {}).get("body")
        elif msg_type in ["image", "video", "audio", "document", "sticker"]:
            media = message.get(msg_type, {})
            unified.update({
                "type": "media",
                "subject": media.get("caption"),
                "body": media.get("id")
            })
        elif msg_type == "button":
            btn = message.get("button", {})
            unified.update({
                "subject": btn.get("text"),
                "body": btn.get("payload")
            })
        elif msg_type == "reaction":
            reaction = message.get("reaction", {})
            unified.update({
                "body": reaction.get("emoji"),
                "origin_msg_id": reaction.get("message_id")
            })

        return unified
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return None
