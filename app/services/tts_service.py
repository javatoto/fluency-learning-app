"""
Text-to-Speech service using OpenAI TTS API with accent support.
"""
from openai import OpenAI
from app.config import settings
import os
from pathlib import Path
import httpx

# Initialize OpenAI client with SSL verification disabled for development
# This is needed when behind corporate proxies with SSL inspection
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.Client(verify=False)
)

# Voice mapping for different accents
ACCENT_VOICE_MAP = {
    "american": "alloy",      # Clear American accent
    "british": "fable",       # British-sounding voice
    "australian": "nova",     # Suitable for Australian accent
}


def get_voice_for_accent(accent: str) -> str:
    """
    Get the appropriate OpenAI voice for a given accent.

    Args:
        accent: Accent type (american, british, australian)

    Returns:
        Voice name for OpenAI TTS
    """
    return ACCENT_VOICE_MAP.get(accent.lower(), "alloy")


def generate_speech(
    text: str,
    accent: str,
    output_path: str,
    model: str = "tts-1"
) -> str:
    """
    Generate speech audio from text using OpenAI TTS.

    Args:
        text: The text to convert to speech
        accent: Accent type (american, british, australian)
        output_path: Path where the audio file should be saved
        model: TTS model to use (tts-1 or tts-1-hd)

    Returns:
        Path to the generated audio file
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Get appropriate voice for accent
        voice = get_voice_for_accent(accent)

        # Generate speech
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3"
        )

        # Save to file
        response.stream_to_file(output_path)

        return output_path

    except Exception as e:
        raise Exception(f"Error generating speech: {str(e)}")


def generate_speech_for_content(
    content_id: str,
    text: str,
    accent: str,
    base_dir: str = None
) -> str:
    """
    Generate speech for practice content and save with content ID.

    Args:
        content_id: Unique content identifier
        text: Text to convert to speech
        accent: Accent type
        base_dir: Base directory for audio storage

    Returns:
        Relative path to the audio file
    """
    if base_dir is None:
        base_dir = settings.AUDIO_STORAGE_PATH

    # Create path: audio_files/tts/{accent}/{content_id}.mp3
    accent_dir = os.path.join(base_dir, "tts", accent.lower())
    os.makedirs(accent_dir, exist_ok=True)

    filename = f"{content_id}.mp3"
    output_path = os.path.join(accent_dir, filename)

    # Generate speech
    generate_speech(text, accent, output_path)

    # Return relative path for storing in database
    relative_path = f"/audio/tts/{accent.lower()}/{filename}"
    return relative_path


def get_available_voices() -> dict:
    """
    Get list of available voices and their accent mappings.

    Returns:
        Dictionary of accent to voice mappings
    """
    return ACCENT_VOICE_MAP.copy()
