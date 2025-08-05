from app.core.ports.output import MetaApiOutputPort
from typing import Dict

class FakeMetaApiAdapter(MetaApiOutputPort):
    def send_message(self, payload: Dict) -> Dict:
            print("[FAKE] Simulando envio para Meta API - Payload:", payload)

            if("status" in payload):
                print("[FAKE] Simulando status de escrita ou leitura")
                return {
                    "success": True,
                }
                
            return {
                "messaging_product": "whatsapp",
                "contacts": [
                    {
                    "input": "<WHATSAPP_USER_PHONE_NUMBER>",
                    "wa_id": "<WHATSAPP_USER_ID>"
                    }
                ],
                "messages": [
                    {
                    "id": "<WHATSAPP_MESSAGE_ID>",
                    "message_status": "<PACING_STATUS>"
                    }
                ]
            }
