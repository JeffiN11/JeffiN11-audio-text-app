# JeffiN11-audio-text-app 🎙️

![CI](https://github.com/JeffiN11/JeffiN11-audio-text-app/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

An AI-powered audio transcription API. Upload any audio file and get a full transcript, automatic summary, sentiment analysis, and speaker detection — all running locally with no API keys needed.

## Features

- 🎙️ **Transcription** — Local speech-to-text via OpenAI Whisper
- 📝 **Summarization** — Auto-summary via Ollama (llama3)
- 😊 **Sentiment Analysis** — Positive / Negative / Neutral scoring
- 🗣️ **Speaker Detection** — Detects multiple speakers
- 📁 **File Support** — mp3, mp4, wav, m4a, ogg, flac, webm (max 50MB)
- 🐘 **PostgreSQL** — Stores all transcriptions
- 🐳 **Docker** — One command to run everything
- ✅ **CI** — GitHub Actions lint and tests

## How It Works

1. Upload an audio file to `POST /transcriptions/`
2. API saves it instantly and returns `status: processing`
3. In the background: Whisper transcribes → Ollama summarizes → Ollama analyzes sentiment
4. Poll `GET /transcriptions/{id}` to get the completed result

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI 0.115 (async) |
| Transcription | OpenAI Whisper (local) |
| Summarization + Sentiment | Ollama + llama3 (local) |
| Database | PostgreSQL 16 + SQLAlchemy 2 |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-asyncio |
| CI | GitHub Actions |

## Quick Start

```bash
git clone https://github.com/JeffiN11/JeffiN11-audio-text-app.git
cd JeffiN11-audio-text-app
docker compose up --build
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /transcriptions/ | Upload audio file |
| GET | /transcriptions/ | List all transcriptions |
| GET | /transcriptions/{id} | Get single transcription |
| DELETE | /transcriptions/{id} | Delete transcription |

## Example

```bash
curl -X POST http://localhost:8000/transcriptions/ \
  -F "file=@meeting.mp3"
```

Response:
```json
{
  "id": 1,
  "filename": "meeting.mp3",
  "status": "processing",
  "transcript": null,
  "summary": null,
  "sentiment": "pending"
}
```

After processing:
```json
{
  "id": 1,
  "filename": "meeting.mp3",
  "status": "completed",
  "transcript": "Good morning everyone, let us get started with the weekly sync...",
  "summary": "A weekly team sync discussing project progress and upcoming deadlines.",
  "sentiment": "positive",
  "sentiment_score": 0.82,
  "speakers_detected": 3,
  "language": "en",
  "duration": 342.5
}
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pip install fastapi uvicorn sqlalchemy asyncpg pydantic httpx python-dotenv python-multipart alembic
pytest -v
```
