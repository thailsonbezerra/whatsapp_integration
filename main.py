from fastapi import FastAPI
from app.adapters.controllers import http, webhook

app = FastAPI()

# Inclui os roteadores
app.include_router(http.router)
app.include_router(webhook.router)
