from typing import Optional
from supabase import Client
from fastapi import HTTPException, status
import logging
from app.models import UserResponse

logger = logging.getLogger(__name__)


async def signup_user(client: Client, email: str, password: str) -> dict:
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })

        if response.user is None:
            logger.error("Signup response user is None")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        return {
            "user_id": response.user.id,
            "email": response.user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        logger.error(f"Signup error: {error_str}")
        if "already registered" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {error_str}"
        )


async def login_user(client: Client, email: str, password: str) -> dict:
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return {
            "access_token": response.session.access_token,
            "user_id": response.user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


async def get_current_user(auth_header: str) -> UserResponse:
    try:
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication header"
            )

        token = parts[1]

        from app.database import get_supabase_client
        client = get_supabase_client()

        user_response = client.auth.get_user(token)

        if user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return UserResponse(
            id=user_response.user.id,
            email=user_response.user.email,
            created_at=user_response.user.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def logout_user(client: Client) -> None:
    try:
        client.auth.sign_out()
    except Exception:
        pass
