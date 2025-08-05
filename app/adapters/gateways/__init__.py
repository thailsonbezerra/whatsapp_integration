from config import AppConfig
from .meta_api import MetaApiAdapter
from .fake_meta_api import FakeMetaApiAdapter

def get_meta_adapter():
    if AppConfig.ENV == "test" or not AppConfig.ACCESS_TOKEN:
        return FakeMetaApiAdapter()
    return MetaApiAdapter()