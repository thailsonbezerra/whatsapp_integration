from dotenv import load_dotenv
import os

load_dotenv()

class AppConfig:
    META_API_URL = os.getenv("META_API_URL", "https://graph.facebook.com/v18.0")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    WABA_PHONE_ID = os.getenv("WABA_PHONE_ID")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    ENV = os.getenv("ENV", "test")
    
    @classmethod
    def validate(cls):
        if not cls.ACCESS_TOKEN or not cls.WABA_PHONE_ID or not cls.VERIFY_TOKEN:
            raise ValueError("Variáveis de ambiente obrigatórias não configuradas.")
