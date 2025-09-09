from fastapi import APIRouter
import logging
logging.basicConfig(level=logging.INFO)
    
router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    logging.info("Health check request received")
    return {"status": "ok"}
