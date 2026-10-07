from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services.tts_service import text_to_speech
from backend.database import audio_collection
from backend.utils.auth import decode_token
from datetime import datetime

router = APIRouter(prefix="/speech", tags=["Speech"])


class SpeechRequest(BaseModel):
    text: str
    voice: str = "aria"
    speed: float = 1.0
    pitch: int = 0
    stability: int = 75
    language: str = "en"
    emotion: str = "neutral"
    format: str = "mp3"


@router.post("/")
def generate_speech(
    request: SpeechRequest,
    authorization: str = Header(...)
):
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    audio_file = text_to_speech(
        text=request.text,
        voice=request.voice,
        speed=request.speed,
        pitch=request.pitch,
        export_format=request.format,
    )

    audio_collection.insert_one({
        "user_id":    payload["user_id"],
        "text":       request.text,
        "voice":      request.voice,
        "format":     request.format,
        "speed":      request.speed,
        "pitch":      request.pitch,
        "audio_file": audio_file,
        "created_at": datetime.utcnow(),
    })

    media_type = "audio/wav" if request.format == "wav" else "audio/mpeg"
    filename = f"speech.{request.format}"

    return FileResponse(
        path=audio_file,
        media_type=media_type,
        filename=filename
    )