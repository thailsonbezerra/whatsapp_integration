from app.adapters.s3.fake_s3_storage_adapter import FakeS3StorageAdapter
from config import AppConfig

def get_s3_adapter():
    if AppConfig.ENV == "test":
        return FakeS3StorageAdapter()
    return S3StorageAdapter()