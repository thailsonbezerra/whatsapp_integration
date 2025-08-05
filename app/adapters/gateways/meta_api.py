from config import AppConfig
from app.core.ports.output import MetaApiOutputPort
from typing import Dict
import requests

class MetaApiAdapter(MetaApiOutputPort):
    def __init__(self):
        self.api_url = AppConfig.META_API_URL
        self.access_token = AppConfig.ACCESS_TOKEN
        self.waba_phone_id = AppConfig.WABA_PHONE_ID

    def send_message(self, payload: Dict) -> Dict:
        url = f"{self.api_url}/{self.waba_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
