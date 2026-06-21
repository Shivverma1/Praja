"""
database.py — Async SQLAlchemy engine + session factory
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./praja.db"
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""
    RAPIDAPI_KEY: str = ""
    GEMINI_API_KEY: str = ""
    APP_MODE: str = "demo"   # "demo" | "live"
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ("backend/.env", ".env")
        extra = "ignore"


settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # NOTE: do NOT pass check_same_thread for aiosqlite — it's handled internally
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    import backend.models  # noqa: F401 — registers all ORM models with Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
