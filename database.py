from supabase import create_client, Client
from app.config import get_settings

_settings = get_settings()


def get_supabase_client() -> Client:
    return create_client(_settings.supabase_url, _settings.supabase_anon_key)
