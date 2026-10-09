from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from supabase import create_client

from app.core.config import (
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def get_auth_client():
    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )


# ============================================
# SIGN UP
# ============================================

@router.post("/signup")
def signup(data: SignupRequest):
    auth_client = get_auth_client()

    try:
        response = auth_client.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Signup failed"
            )

        return {
            "message": "User created successfully",
            "user_id": response.user.id,
            "email": response.user.email,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================
# LOGIN
# ============================================

@router.post("/login")
def login(data: LoginRequest):
    auth_client = get_auth_client()

    try:
        response = auth_client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })

        if response.user is None or response.session is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        return {
            "message": "Login successful",
            "user_id": response.user.id,
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )