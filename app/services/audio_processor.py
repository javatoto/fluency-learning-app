"""
Audio file processing service for format conversion and storage.
"""
import os
from pydub import AudioSegment
from pathlib import Path
from app.config import settings


def convert_webm_to_wav(input_path: str, output_path: str) -> str:
    """
    Convert WebM audio to WAV format.

    Args:
        input_path: Path to input WebM file
        output_path: Path for output WAV file

    Returns:
        Path to converted WAV file
    """
    try:
        # Load audio file
        audio = AudioSegment.from_file(input_path, format="webm")

        # Export as WAV (16kHz, mono for Whisper optimization)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")

        return output_path

    except Exception as e:
        raise Exception(f"Error converting audio: {str(e)}")


def save_uploaded_audio(
    audio_data: bytes,
    user_id: str,
    recording_id: str,
    format: str = "webm"
) -> str:
    """
    Save uploaded audio file to storage.

    Args:
        audio_data: Raw audio bytes
        user_id: User ID
        recording_id: Recording ID
        format: Audio format

    Returns:
        Path to saved file
    """
    # Create directory structure: audio_files/recordings/{user_id}/
    user_dir = os.path.join(settings.AUDIO_STORAGE_PATH, "recordings", user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Save original file
    filename = f"{recording_id}.{format}"
    file_path = os.path.join(user_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(audio_data)

    return file_path


def convert_user_recording(webm_path: str, recording_id: str) -> str:
    """
    Convert user recording from WebM to WAV for Whisper processing.

    Args:
        webm_path: Path to WebM file
        recording_id: Recording ID

    Returns:
        Path to WAV file
    """
    # Generate WAV path in same directory
    wav_path = webm_path.replace('.webm', '.wav')

    # Convert
    convert_webm_to_wav(webm_path, wav_path)

    return wav_path


def get_audio_duration(file_path: str) -> float:
    """
    Get duration of audio file in seconds.

    Args:
        file_path: Path to audio file

    Returns:
        Duration in seconds
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        raise Exception(f"Error getting audio duration: {str(e)}")
