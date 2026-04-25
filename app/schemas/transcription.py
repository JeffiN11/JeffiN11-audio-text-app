from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.transcription import SentimentLabel, TranscriptionStatus


class TranscriptionResponse(BaseModel):
    id: int
    filename: str
    file_size: Optional[int]
    duration: Optional[float]
    status: TranscriptionStatus
    transcript: Optional[str]
    summary: Optional[str]
    sentiment: SentimentLabel
    sentiment_score: Optional[float]
    speakers_detected: Optional[int]
    language: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TranscriptionListResponse(BaseModel):
    total: int
    transcriptions: list[TranscriptionResponse]
