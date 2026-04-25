from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.routers import transcriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Audio Text API",
    description="AI-powered audio transcription API. Upload audio files and get transcripts, summaries, sentiment analysis, and speaker detection automatically.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcriptions.router, prefix="/transcriptions", tags=["Transcriptions"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Audio Text API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
