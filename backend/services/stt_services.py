import os
import tempfile
from datetime import datetime

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from backend.database import transcript_collection
from backend.services.stt_service import speech_to_text
from backend.utils.auth import decode_token

router = APIRouter(prefix="/stt", tags=["Speech to Text"])

MAX_UPLOAD_MB = 25


def _user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        return decode_token(token)["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/")
def transcribe(
    file: UploadFile = File(...),
    language: str = Form(""),
    authorization: str = Header(...)
):
    user_id = _user_id(authorization)

    data = file.file.read()

    if not data:
        raise HTTPException(status_code=400, detail="The audio file is empty")

    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file is larger than {MAX_UPLOAD_MB} MB"
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        result = speech_to_text(tmp_path, language or None)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this audio. Try MP3, WAV, M4A, OGG or WEBM."
        )
    finally:
        os.remove(tmp_path)

    transcript_collection.insert_one({
        "user_id": user_id,
        "text": result["text"],
        "language": result["language"],
        "duration": result["duration"],
        "filename": file.filename,
        "created_at": datetime.utcnow(),
    })

    return result


@router.get("/history")
def transcript_history(authorization: str = Header(...)):
    user_id = _user_id(authorization)

    items = transcript_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(50)

    return [
        {
            "id": str(item["_id"]),
            "text": item["text"],
            "language": item.get("language"),
            "duration": item.get("duration"),
            "filename": item.get("filename"),
            "created_at": item["created_at"].isoformat() + "Z",
        }
        for item in items
    ]
