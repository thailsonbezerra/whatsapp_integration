from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    print("Health check request received")
    return {"status": "ok"}
