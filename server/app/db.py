from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import get_settings


class Database:
    _client: Optional[AsyncIOMotorClient] = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            settings = get_settings()
            # Use certifi CA bundle for proper TLS on deployed environments (Render, etc.)
            try:
                import certifi
                ca = certifi.where()
            except ImportError:
                ca = None

            kwargs = {
                "serverSelectionTimeoutMS": 10000,
                "connectTimeoutMS": 10000,
                "tls": True,
                "tlsAllowInvalidCertificates": False,
            }
            if ca:
                kwargs["tlsCAFile"] = ca

            cls._client = AsyncIOMotorClient(settings.mongodb_uri, **kwargs)
        return cls._client

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        settings = get_settings()
        return cls.get_client()[settings.mongodb_db]


def get_db() -> AsyncIOMotorDatabase:
    return Database.get_db()
