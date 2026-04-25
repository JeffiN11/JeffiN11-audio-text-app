from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db, AsyncSessionLocal
from app.models.transcription import Transcription, TranscriptionStatus, SentimentLabel
from app.schemas.transcription import TranscriptionResponse, TranscriptionListResponse
from app.services.whisper_service import transcribe_audio
from app.services.ollama_service import get_summary, get_sentiment
from app.services.speaker_service import detect_speakers

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


async def _process_audio(transcription_id: int, file_bytes: bytes, filename: str):
    """Background task: transcribe + summarize + sentiment analysis."""
    async with AsyncSessionLocal() as session:
        record = await session.get(Transcription, transcription_id)
        if not record:
            return

        try:
            # Step 1: Transcribe with Whisper
            result = await transcribe_audio(file_bytes, filename)
            transcript = result["transcript"]

            record.transcript = transcript
            record.language = result["language"]
            record.duration = result["duration"]

            # Step 2: Summarize with Ollama
            if transcript:
                record.summary = await get_summary(transcript)

            # Step 3: Sentiment analysis with Ollama
            if transcript:
                sentiment_result = await get_sentiment(transcript)
                record.sentiment = SentimentLabel(sentiment_result["sentiment"])
                record.sentiment_score = sentiment_result["score"]

            # Step 4: Speaker detection
            record.speakers_detected = detect_speakers(transcript)

            record.status = TranscriptionStatus.completed

        except Exception as e:
            record.status = TranscriptionStatus.failed
            record.transcript = f"Processing failed: {str(e)}"

        await session.commit()


@router.post("/", response_model=TranscriptionResponse, status_code=201)
async def create_transcription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an audio file. Transcription + summarization + sentiment analysis
    run in the background. Returns immediately with status='processing'.
    Supported: mp3, mp4, wav, m4a, ogg, flac, webm (max 50MB).
    """
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    record = Transcription(
        filename=file.filename,
        file_size=len(file_bytes),
        status=TranscriptionStatus.processing,
        sentiment=SentimentLabel.pending,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    background_tasks.add_task(_process_audio, record.id, file_bytes, file.filename)

    return record


@router.get("/", response_model=TranscriptionListResponse)
async def list_transcriptions(
    db: AsyncSession = Depends(get_db),
):
    """List all transcriptions."""
    count_query = select(func.count(Transcription.id))
    query = select(Transcription).order_by(Transcription.created_at.desc())

    total = (await db.execute(count_query)).scalar_one()
    records = (await db.execute(query)).scalars().all()

    return TranscriptionListResponse(total=total, transcriptions=list(records))


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(transcription_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single transcription by ID."""
    record = await db.get(Transcription, transcription_id)
    if not record:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return record


@router.delete("/{transcription_id}", status_code=204)
async def delete_transcription(transcription_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a transcription by ID."""
    record = await db.get(Transcription, transcription_id)
    if not record:
        raise HTTPException(status_code=404, detail="Transcription not found")
    await db.delete(record)
    await db.commit()
