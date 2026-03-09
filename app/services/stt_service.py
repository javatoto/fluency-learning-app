"""
Speech-to-Text service using OpenAI Whisper API.
"""
from openai import OpenAI
from app.config import settings
import httpx

# Initialize OpenAI client with SSL verification disabled for development
# This is needed when behind corporate proxies with SSL inspection
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.Client(verify=False)
)


def transcribe_audio(audio_file_path: str, language: str = "en") -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file_path: Path to audio file (WAV, MP3, etc.)
        language: Language code (default: "en")

    Returns:
        Transcribed text
    """
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text"
            )

        return transcript.strip()

    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")


def transcribe_with_timestamps(audio_file_path: str, language: str = "en") -> dict:
    """
    Transcribe audio with word-level timestamps.

    Args:
        audio_file_path: Path to audio file
        language: Language code

    Returns:
        Dictionary with text and segments
    """
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        return {
            "text": transcript.text,
            "duration": transcript.duration,
            "words": transcript.words if hasattr(transcript, 'words') else []
        }

    except Exception as e:
        raise Exception(f"Error transcribing with timestamps: {str(e)}")
