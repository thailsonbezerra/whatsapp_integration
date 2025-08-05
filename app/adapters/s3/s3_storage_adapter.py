import os
from typing import BinaryIO

from app.core.ports.output import FileStoragePort

class S3StorageAdapter(FileStoragePort):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def upload_file(self, file_data: BinaryIO, filename: str, content_type: str) -> str:
        return ""
