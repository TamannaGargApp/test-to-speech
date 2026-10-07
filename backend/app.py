from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth_routes import router as auth_router
from backend.routes.speech_routes import router as speech_router
from backend.routes.history_routes import router as history_router

app = FastAPI(
    title="Text To Speech API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router
)

app.include_router(
    speech_router
)

app.include_router(
    history_router
)