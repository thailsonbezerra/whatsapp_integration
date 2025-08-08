import os
from typing import BinaryIO

from app.core.ports.output import FileStoragePort

class S3StorageAdapter(FileStoragePort):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def upload_file(self, file_data: BinaryIO, filename: str) -> str:
        folder = 'medias'
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, filename)
        with open(file_path, "wb") as f:
            f.write(file_data.read())
        print(f"Arquivo salvo em: {file_path}")
        return file_path
