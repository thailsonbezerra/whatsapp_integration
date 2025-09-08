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
        return response.json()

    def get_media_url(self, media_id: str) -> str:
        url = f"{self.api_url}/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.get(url, headers=headers)

        return response.json()
        
    def download_media(self, media_url: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(media_url, headers=headers)
        # Extrair o nome do arquivo do header 'Content-Disposition'
        content_disposition = response.headers.get("Content-Disposition")
        file_name = None
        if content_disposition:
            parts = content_disposition.split(";")
            for part in parts:
                if "filename=" in part:
                    file_name = part.split("=")[1].strip().strip('"')
                    break
        
        return {
            "content": response.content,
            "filename": file_name,
        }