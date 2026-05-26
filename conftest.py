import pytest
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    def _auth_headers(token: str):
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers
