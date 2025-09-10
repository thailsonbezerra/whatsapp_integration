import logging
logging.basicConfig(level=logging.INFO)

def normalize_webhook_event(payload, phone_number_waba):
    normalized = {
        "recipient": "",
        "sender_name": "",
        "sender": "",
        "channel_message_id": "",
        "timestamp": "",
        "subject": "",
        "body": "",
        "message_type": "",
        "event_type": "",
        "channel_type": "whatsapp",
        "reference_channel_message_id": "",
    }

    logging.info("==========================================================")
    if "errors" in payload:
        logging.info("Normalizing error event...")
        return _normalize_error_event(payload, normalized)
    elif "statuses" in payload:
        logging.info("Normalizing status event...")
        return _normalize_status_event(payload, normalized, phone_number_waba)
    elif "messages" in payload:
        logging.info("Normalizing message event...")
        return _normalize_message_event(payload, normalized, phone_number_waba)

    logging.info("===========================================================")
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
            "channel_message_id": payload.get("id"),
            "sender": payload.get("from")
        })
        logging.info(f"Normalized error event: {normalized}")
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
                "channel_message_id": status.get("id"),
                "event_type": "error",
                "subject": f"{error.get('code')} {error.get('title')}",
                "body": error.get("error_data").get("details"),
                "recipient": phone_number_waba,
                "sender": status.get("recipient_id"),
                "message_type": "failed",
            })
            logging.info(f"Normalized status error event: {normalized}")
            return normalized
        
        normalized.update({
            "channel_message_id": status.get("id"),
            "event_type": "status",
            "timestamp": status.get("timestamp"),
            "recipient": phone_number_waba,
            "sender": status.get("recipient_id"),
            "message_type": status.get("status"),
        })

        logging.info(f"Normalized status event: {normalized}")
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
            "channel_message_id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "sender": message.get("from"),
            "sender_name": profile.get("name"),
            "recipient": phone_number_waba,
            "reference_channel_message_id": context.get("id") if context else "",
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
                "reference_channel_message_id": reaction.get("message_id")
            })

        print(normalized)
        return normalized
    except Exception as e:
        return None
