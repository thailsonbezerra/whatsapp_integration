import os
from typing import BinaryIO

from app.core.ports.output import FileStoragePort

class FakeS3StorageAdapter(FileStoragePort):
    def __init__(self, base_path: str = "tmp/fake_s3"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def upload_file(self, file_data: BinaryIO, filename: str, content_type: str) -> str:
        file_path = os.path.join(self.base_path, filename)

        with open(file_path, "wb") as f:
            f.write(file_data.read())

        print("Simulando upload de arquivo para o S3")
        print(f"Arquivo salvo em: {file_path}")
        # Simula a URL pública
        return f"http://localhost/fake-s3/{filename}"
