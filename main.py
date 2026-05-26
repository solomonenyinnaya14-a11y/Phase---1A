import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import get_supabase_client
from app.models import (
    UserSignup,
    UserLogin,
    UserResponse,
    AuthResponse,
    MessageResponse,
    SubscriptionResponse
)
from app.auth_service import (
    signup_user,
    login_user,
    get_current_user,
    logout_user
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MyStudyApp Backend")
    yield
    logger.info("Shutting down MyStudyApp Backend")


app = FastAPI(
    title="MyStudyApp API",
    description="Backend API for Nigerian Study App",
    version="0.1.0",
    lifespan=lifespan
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response


@app.get("/health", response_model=MessageResponse)
async def health_check():
    return MessageResponse(message="OK")


@app.post("/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignup):
    try:
        client = get_supabase_client()

        result = await signup_user(client, payload.email, payload.password)

        user_data_response = client.table("users").select("*").eq("id", result["user_id"]).single().execute()

        if not user_data_response.data:
            logger.error("User created in Auth but not in users table - trigger may have failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but record fetch failed"
            )

        user_data = user_data_response.data
        return UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            created_at=user_data["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@app.post("/auth/login", response_model=AuthResponse)
async def login(payload: UserLogin):
    client = get_supabase_client()
    result = await login_user(client, payload.email, payload.password)
    return AuthResponse(access_token=result["access_token"])


@app.get("/auth/me", response_model=UserResponse)
async def get_me(authorization: str = Header(...)):
    return await get_current_user(authorization)


@app.post("/auth/logout", response_model=MessageResponse)
async def logout(authorization: str = Header(...)):
    await get_current_user(authorization)
    client = get_supabase_client()
    await logout_user(client)
    return MessageResponse(message="Successfully logged out")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
