import os
import logging
import tempfile
import warnings

logger = logging.getLogger(__name__)

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


def get_whisper_model():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import whisper
        model = whisper.load_model(WHISPER_MODEL)
    return model


async def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    """
    Transcribe audio using OpenAI Whisper (runs locally).
    Returns transcript text, language, and duration.
    """
    try:
        with tempfile.NamedTemporaryFile(
            suffix=os.path.splitext(filename)[1] or ".wav",
            delete=False,
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        model = get_whisper_model()
        result = model.transcribe(tmp_path, fp16=False)

        os.unlink(tmp_path)

        return {
            "transcript": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "duration": result.get("segments", [{}])[-1].get("end", 0.0)
            if result.get("segments")
            else 0.0,
        }

    except Exception as e:
        logger.error("Whisper transcription failed: %s", e)
        raise
