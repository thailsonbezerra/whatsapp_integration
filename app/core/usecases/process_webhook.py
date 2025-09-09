from app.adapters.mappers.webhook_normalizer import normalize_webhook_event
from app.core.ports.input import ProcessWebhookPort
from app.core.ports.output import FileStoragePort
from app.core.ports.output import MetaApiOutputPort
import logging
logging.basicConfig(level=logging.INFO)

from io import BytesIO

class ProcessWebhookUseCase(ProcessWebhookPort):
    def __init__(self, storage: FileStoragePort, meta_api: MetaApiOutputPort):
        self.storage = storage
        self.meta_api = meta_api

    def execute(self, waba_id, payload: dict) -> dict:
        phone_number_id_waba = payload.get("metadata", {}).get("phone_number_id")
        phone_number_waba = payload.get("metadata", {}).get("display_phone_number")
        print(payload)
        logging.info("=========================================================")
        logging.info(f"Received webhook for WABA ID: {waba_id}, Phone Number: {phone_number_waba}, Payload: {payload}")
        logging.info("=========================================================")
        normalized = normalize_webhook_event(payload, phone_number_waba)
        # if normalized["type"] == "media":
        #     print("Processing media message...")
        #     media_id = normalized["body"]
            
        #     media = self.meta_api.get_media_url(media_id)
            
        #     print(f"Media details: {media}")
            
        #     if not media:
        #         raise Exception(f"Media not found for ID: {media_id}")
            
        #     media_url = media.get("url")
            
        #     media = self.meta_api.download_media(media_url)
            
        #     if not media:
        #         raise Exception(f"Failed to download media from URL: {media_url}")

        #     uploaded_file_path = self.storage.upload_file(BytesIO(media["content"]), media["filename"]) 
        #     normalized.update({
        #         "media": {
        #             "body": uploaded_file_path,
        #         }
        #     })
        return normalized
