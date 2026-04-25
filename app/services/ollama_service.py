import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

SUMMARY_PROMPT = """You are an expert summarizer. Read the transcript below and provide a concise summary in 2-3 sentences.

Transcript:
{transcript}

Respond ONLY with the summary text. No preamble, no labels."""

SENTIMENT_PROMPT = """You are a sentiment analysis expert. Analyze the sentiment of the transcript below.

Transcript:
{transcript}

Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{{
  "sentiment": "positive" | "negative" | "neutral",
  "score": 0.0 to 1.0,
  "reasoning": "One sentence explaining why."
}}"""


async def get_summary(transcript: str) -> str:
    prompt = SUMMARY_PROMPT.format(transcript=transcript[:3000])
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
    except Exception as e:
        logger.warning("Summary generation failed: %s", e)
        return "Summary unavailable — AI service unreachable."


async def get_sentiment(transcript: str) -> dict:
    prompt = SENTIMENT_PROMPT.format(transcript=transcript[:3000])
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()
            result = json.loads(raw)
            sentiment = result.get("sentiment", "neutral").lower()
            if sentiment not in ("positive", "negative", "neutral"):
                sentiment = "neutral"
            return {
                "sentiment": sentiment,
                "score": float(result.get("score", 0.5)),
            }
    except Exception as e:
        logger.warning("Sentiment analysis failed: %s", e)
        return {"sentiment": "neutral", "score": 0.5}
