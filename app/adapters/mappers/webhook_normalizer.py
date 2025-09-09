from typing import Dict, Optional

def normalize_webhook_event(payload: Dict, phone_number_waba: str) -> Optional[Dict]:
    normalized = {
        "recipient": "",
        "sender_name": "",
        "sender": "",
        "message_id": "",
        "timestamp": "",
        "subject": "",
        "body": "",
        "message_type": "",
        "event_type": "",
        "channel_type": "whatsapp",
        "origin_msg_id": "",
    }

    print("==========================================================")
    if "errors" in payload:
        print("Normalizing error event...")
        return _normalize_error_event(payload, normalized)
    elif "statuses" in payload:
        print("Normalizing status event...")
        return _normalize_status_event(payload, normalized, phone_number_waba)
    elif "messages" in payload:
        print("Normalizing message event...")
        return _normalize_message_event(payload, normalized, phone_number_waba)

    print("===========================================================")
    return None

def _normalize_error_event(payload, normalized):
    try:
        error = payload["errors"][0]
        normalized.update({
            "event_type": "error",
            "timestamp": payload.get("timestamp"),
            "subject": error.get("title"),
            "body": error.get("message"),
            "message_type": "failed",
            "message_id": payload.get("id"),
            "sender": payload.get("from")
        })
        print(normalized)
        return normalized
    except Exception:
        return None

def _normalize_status_event(payload, normalized, phone_number_waba):
    try:
        status = payload["statuses"][0]
        
        #code 131047 janela fechada
        errors = status.get("errors")
        if errors:
            error = errors[0]
            normalized.update({
                "event_type": "error",
                "subject": f"{error.get('code')} {error.get('title')}",
                "body": error.get("error_data").get("details"),
                "message_type": "failed",
                "message_id": status.get("id"),
                "sender": phone_number_waba
            })
            print(normalized)
            return normalized
        
        normalized.update({
            "event_type": "status",
            "message_id": status.get("id"),
            "timestamp": status.get("timestamp"),
            "sender": phone_number_waba,
            "recipient": status.get("recipient_id"),
            "message_type": status.get("status"),
        })
            
        print(normalized)
        return normalized
    except Exception:
        return None

def _normalize_message_event(payload, normalized, phone_number_waba):
    try:
        contact = payload["contacts"][0]
        profile = contact.get("profile", {})
        
        message = payload["messages"][0]
        msg_type = message.get("type")
        context = message.get("context", {})

        normalized.update({
            "event_type": "message",
            "message_id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "sender": message.get("from"),
            "sender_name": profile.get("name"),
            "recipient": phone_number_waba,
            "origin_msg_id": context.get("id") if context else "",
            "message_type": msg_type
        })

        if msg_type == "text":
            normalized["body"] = message.get("text", {}).get("body")
        elif msg_type in ["image", "video", "audio", "document", "sticker"]:
            media = message.get(msg_type, {})
            normalized.update({
                "message_type": "media",
                "subject": media.get("caption"),
                "body": media.get("id")
            })
        elif msg_type == "button":
            btn = message.get("button", {})
            normalized.update({
                "subject": btn.get("text"),
                "body": btn.get("payload")
            })
        elif msg_type == "reaction":
            reaction = message.get("reaction", {})
            normalized.update({
                "body": reaction.get("emoji"),
                "origin_msg_id": reaction.get("message_id")
            })

        print(normalized)
        return normalized
    except Exception as e:
        return None
