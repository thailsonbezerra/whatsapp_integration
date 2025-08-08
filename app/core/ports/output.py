from abc import ABC, abstractmethod
from typing import Dict

class MetaApiOutputPort(ABC):
    @abstractmethod
    def send_message(self, payload: Dict) -> Dict:
        pass
    
    @abstractmethod
    def get_media_url(self, media_id: str) -> str:
        pass

    @abstractmethod
    def download_media(self, media_url: str) -> bytes:
        pass
    
# TODO: Mover FileStoragePort para um local mais apropriado
class FileStoragePort(ABC):
    @abstractmethod
    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        pass