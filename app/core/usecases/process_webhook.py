from app.adapters.mappers.webhook_normalizer import normalize_webhook_event
from app.core.ports.input import ProcessWebhookPort
from app.core.ports.output import FileStoragePort
from app.core.ports.output import MetaApiOutputPort

from io import BytesIO

class ProcessWebhookUseCase(ProcessWebhookPort):
    def __init__(self, storage: FileStoragePort, meta_api: MetaApiOutputPort):
        self.storage = storage
        self.meta_api = meta_api

    def execute(self, waba_id, payload: dict) -> dict:
        print("=========================================================")
        print(f"Processing webhook for WABA ID: {waba_id}")
        
        phone_number_id_waba = payload.get("metadata", {}).get("phone_number_id")
        phone_number_waba = payload.get("metadata", {}).get("display_phone_number")
        normalized = normalize_webhook_event(payload, phone_number_waba)
        
        print(f"Webhook normalizado: {normalized}")

        if normalized["type"] in ["image", "video", "audio", "document", "sticker"]:
            media_id = normalized["body"]
            
            media_url = self.meta_api.get_media_url(media_id)
            if not media_url:
                raise ValueError(f"Media URL not found for media_id: {media_id}")
            
            print(f"Baixando mídia de: {media_url}")
            media = self.meta_api.download_media(media_url)
            file_obj = BytesIO(media["content"])
            filename = f"{media_id}.{media['extension']}"
            #TODO: Decidir se retorna a url do s3 ou o id da midia?
            self.storage.upload_file(file_obj, filename, media["content_type"])
            
        return normalized
