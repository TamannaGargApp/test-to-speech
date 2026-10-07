import json
import os
import urllib.error
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from backend.database import users_collection
from backend.utils.security import (
    hash_password,
    verify_password
)

from backend.utils.auth import create_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


# Public OAuth client ID (same as GOOGLE_CLIENT_ID in frontend/auth.js).
# Set GOOGLE_CLIENT_ID in .env to override it.
DEFAULT_GOOGLE_CLIENT_ID = "210393640285-40g457h3e83gaanjsjr1eh7hlqumk4l7.apps.googleusercontent.com"

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


def verify_google_id_token(token: str, client_id: str) -> dict:
    """Ask Google to check the ID token (signature and expiry), then check
    it was issued for this app. Raises ValueError if it is not valid."""

    url = GOOGLE_TOKENINFO_URL + "?" + urllib.parse.urlencode({"id_token": token})

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            info = json.load(resp)
    except urllib.error.HTTPError:
        raise ValueError("Google rejected the token")
    except urllib.error.URLError as exc:
        raise ValueError(f"Could not reach Google: {exc.reason}")

    if info.get("aud") != client_id:
        raise ValueError("Token was issued for a different client ID")

    if info.get("iss") not in GOOGLE_ISSUERS:
        raise ValueError("Token was not issued by Google")

    return info


class GoogleLoginRequest(BaseModel):
    id_token: str
    nonce: str


@router.post("/register")
def register(request: RegisterRequest):

    existing_user = users_collection.find_one(
        {"email": request.email}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = {
        "email": request.email,
        "password": hash_password(
            request.password
        )
    }

    result = users_collection.insert_one(
        user
    )

    return {
        "message": "User created",
        "user_id": str(result.inserted_id)
    }


@router.post("/login")
def login(request: RegisterRequest):

    user = users_collection.find_one(
        {"email": request.email}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Accounts created with Google sign-in have no password
    if not user.get("password"):
        raise HTTPException(
            status_code=401,
            detail="This account uses Google sign-in"
        )

    if not verify_password(
        request.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token(
        str(user["_id"])
    )

    return {
        "access_token": token
    }


@router.post("/google")
def google_login(request: GoogleLoginRequest):

    client_id = os.getenv("GOOGLE_CLIENT_ID") or DEFAULT_GOOGLE_CLIENT_ID

    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="Google sign-in is not configured"
        )

    # Checks Google's signature, the audience (our client ID) and expiry
    try:
        info = verify_google_id_token(
            request.id_token,
            client_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {exc}"
        )

    if info.get("nonce") != request.nonce:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )

    if str(info.get("email_verified")).lower() != "true":
        raise HTTPException(
            status_code=401,
            detail="Google email is not verified"
        )

    email = info["email"]
    google_sub = info["sub"]

    user = users_collection.find_one(
        {"email": email}
    )

    if user:
        if user.get("google_sub") and user["google_sub"] != google_sub:
            raise HTTPException(
                status_code=401,
                detail="Invalid Google account"
            )

        if not user.get("google_sub"):
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"google_sub": google_sub}}
            )

        user_id = str(user["_id"])

    else:
        result = users_collection.insert_one({
            "email": email,
            "google_sub": google_sub
        })

        user_id = str(result.inserted_id)

    return {
        "access_token": create_token(user_id),
        "email": email
    }
