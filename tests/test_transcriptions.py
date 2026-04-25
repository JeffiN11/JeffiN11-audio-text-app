import pytest
from unittest.mock import patch, AsyncMock
import io

MOCK_TRANSCRIBE = {
    "transcript": "Hello this is a test audio recording.",
    "language": "en",
    "duration": 5.0,
}
MOCK_SUMMARY = "This is a test audio recording used for unit testing."
MOCK_SENTIMENT = {"sentiment": "positive", "score": 0.85}


def make_audio_file(filename="test.wav"):
    return {"file": (filename, io.BytesIO(b"fake audio content"), "audio/wav")}


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_upload_audio(client):
    with patch("app.routers.transcriptions.transcribe_audio", new_callable=AsyncMock) as mock_t, \
         patch("app.routers.transcriptions.get_summary", new_callable=AsyncMock) as mock_s, \
         patch("app.routers.transcriptions.get_sentiment", new_callable=AsyncMock) as mock_sent:
        mock_t.return_value = MOCK_TRANSCRIBE
        mock_s.return_value = MOCK_SUMMARY
        mock_sent.return_value = MOCK_SENTIMENT

        response = await client.post("/transcriptions/", files=make_audio_file())

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.wav"
    assert data["status"] == "processing"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_upload_invalid_format(client):
    response = await client.post(
        "/transcriptions/",
        files={"file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_transcription(client):
    response = await client.post("/transcriptions/", files=make_audio_file())
    transcription_id = response.json()["id"]

    get_response = await client.get(f"/transcriptions/{transcription_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == transcription_id


@pytest.mark.asyncio
async def test_get_transcription_not_found(client):
    response = await client.get("/transcriptions/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_transcriptions(client):
    await client.post("/transcriptions/", files=make_audio_file("audio1.wav"))
    await client.post("/transcriptions/", files=make_audio_file("audio2.mp3"))

    response = await client.get("/transcriptions/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["transcriptions"]) == 2


@pytest.mark.asyncio
async def test_delete_transcription(client):
    response = await client.post("/transcriptions/", files=make_audio_file())
    transcription_id = response.json()["id"]

    delete_response = await client.delete(f"/transcriptions/{transcription_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/transcriptions/{transcription_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_speaker_detection():
    from app.services.speaker_service import detect_speakers
    single = detect_speakers("This is a single speaker transcript.")
    assert single == 1

    multi = detect_speakers("Speaker 1: Hello\nSpeaker 2: Hi there")
    assert multi >= 2
