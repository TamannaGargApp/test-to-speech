from fastapi import APIRouter
from fastapi import Header

from backend.database import (
    audio_collection
)

from backend.utils.auth import (
    decode_token
)

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/")
def get_history(
    authorization: str = Header(...)
):

    token = authorization.replace(
        "Bearer ",
        ""
    )

    payload = decode_token(token)

    history = []

    for item in audio_collection.find(
        {
            "user_id":
                payload["user_id"]
        }
    ):
        history.append({
            "id":
                str(item["_id"]),
            "text":
                item["text"],
            "audio_file":
                item["audio_file"]
        })

    return history