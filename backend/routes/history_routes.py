import os

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse

from backend.database import audio_collection
from backend.utils.auth import decode_token

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


def _user_id(authorization: str) -> str:
    try:
        return decode_token(authorization.replace("Bearer ", ""))["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/")
def get_history(
    authorization: str = Header(...)
):

    user_id = _user_id(authorization)

    history = []

    for item in audio_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1):
        created = item.get("created_at")
        history.append({
            "id": str(item["_id"]),
            "text": item["text"],
            "voice": item.get("voice", "aria"),
            "format": item.get("format", "mp3"),
            "audio_file": item["audio_file"],
            "created_at": created.isoformat() + "Z" if created else None,
        })

    return history


@router.get("/{item_id}/audio")
def get_history_audio(
    item_id: str,
    authorization: str = Header(...)
):

    user_id = _user_id(authorization)

    try:
        item = audio_collection.find_one(
            {"_id": ObjectId(item_id), "user_id": user_id}
        )
    except InvalidId:
        item = None

    if not item or not os.path.exists(item["audio_file"]):
        raise HTTPException(status_code=404, detail="Audio file not found")

    is_wav = item["audio_file"].endswith(".wav")

    return FileResponse(
        item["audio_file"],
        media_type="audio/wav" if is_wav else "audio/mpeg"
    )
