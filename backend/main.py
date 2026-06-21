"""
main.py — FastAPI application entrypoint
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db, settings
from backend.routers import creator, posts, audience


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Praja Creator Intelligence Module",
    description="Full-stack creator analytics API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(creator.router)
app.include_router(posts.router)
app.include_router(audience.router)


@app.get("/")
async def root():
    return {"message": "Praja Creator Intelligence API", "version": "1.0.0", "mode": settings.APP_MODE}


@app.get("/health")
async def health():
    return {"status": "ok"}
