import logging

logger = logging.getLogger(__name__)


def detect_speakers(transcript: str) -> int:
    """
    Simple heuristic speaker detection based on transcript patterns.
    In production this would use pyannote.audio for real diarization.
    """
    if not transcript:
        return 1

    indicators = [
        "Speaker 1:", "Speaker 2:", "Speaker A:", "Speaker B:",
        "[Speaker", "SPEAKER_", ": ", " - ",
    ]

    speaker_count = 1
    for indicator in indicators:
        if indicator in transcript:
            speaker_count = max(speaker_count, 2)
            break

    lines = transcript.split("\n")
    unique_prefixes = set()
    for line in lines:
        if ":" in line:
            prefix = line.split(":")[0].strip()
            if len(prefix) < 30:
                unique_prefixes.add(prefix.lower())

    if len(unique_prefixes) >= 2:
        speaker_count = min(len(unique_prefixes), 10)

    return speaker_count
