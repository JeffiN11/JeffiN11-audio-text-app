from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.database import Base


class SentimentLabel(str, enum.Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    pending = "pending"


class TranscriptionStatus(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[TranscriptionStatus] = mapped_column(
        SAEnum(TranscriptionStatus),
        default=TranscriptionStatus.processing,
        nullable=False,
    )
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    sentiment: Mapped[SentimentLabel] = mapped_column(
        SAEnum(SentimentLabel),
        default=SentimentLabel.pending,
        nullable=False,
    )
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    speakers_detected: Mapped[int] = mapped_column(nullable=True)
    language: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
