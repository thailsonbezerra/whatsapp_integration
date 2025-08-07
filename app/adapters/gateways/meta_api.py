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
        print("========================================================")
        url = f"{self.api_url}/{self.waba_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Sending payload to Meta API: {payload}")  # Debugging line
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response from Meta API: {response.json()}")  # Debugging line
        print("========================================================")
        return response.json()

    def get_media_url(self, media_id: str) -> str:
        url = f"{self.api_url}/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("url")
        
    def download_media(self, media_url: str) -> bytes:
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(media_url, headers=headers)
        response.raise_for_status()
        return response.content