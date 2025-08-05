from app.core.ports.output import MetaApiOutputPort
from typing import Dict
import json

class FakeMetaApiAdapter(MetaApiOutputPort):
    def send_message(self, payload: Dict) -> Dict:
            print("[FAKE] Simulando envio para Meta API - Payload:")
            pretty_json = json.dumps(payload, indent=4)
            print(pretty_json)

            if("status" in payload):
                print("[FAKE] Simulando status de escrita ou leitura")
                return {
                    "success": True,
                }
                
            return {
                "messaging_product": "whatsapp",
                "contacts": [
                    {
                    "input": payload.get("to"),
                    "wa_id": "wa.fake.id123456"
                    }
                ],
                "messages": [
                    {
                    "id": "wa_fake_message_id_123456",
                    "message_status": "sent"
                    }
                ]
            }

    def get_media_url(self, media_id):
        print(f"[FAKE] Simulando obtenção de URL de mídia com ID: {media_id}")
        return f"http://fake-media-url.com/{media_id}"
     
    def download_media(self, meta_url: str) -> dict:
        print(f"[FAKE] Simulando download de mídia com ID: {meta_url}")
        return {
            "content": b"Fake media content",
            "content_type": "image/jpeg",
            "extension": "jpg",
        }