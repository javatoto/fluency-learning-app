"""
Recording upload and pronunciation analysis routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recording import RecordingResponse
from app.models.recording import Recording
from app.models.content import Content
from app.services import audio_processor, stt_service, pronunciation_service, progress_service
from app.routes.auth import get_current_user_dependency
from app.models.user import User
import os
import tempfile

router = APIRouter(prefix="/api/recordings", tags=["recordings"])


@router.post("", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def create_recording(
    audio: UploadFile = File(...),
    content_id: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Upload user recording and analyze pronunciation.

    Steps:
    1. Get current user from session
    2. Save uploaded audio file
    3. Convert to WAV format
    4. Transcribe using Whisper
    5. Analyze pronunciation
    6. Save results to database
    """
    # Get current user from session
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Validate content exists
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    try:
        # Create recording record
        recording = Recording(
            user_id=user_id,
            content_id=content_id
        )
        db.add(recording)
        db.flush()  # Get ID

        # Read audio data
        audio_data = await audio.read()

        # Save uploaded file
        webm_path = audio_processor.save_uploaded_audio(
            audio_data=audio_data,
            user_id=user_id,
            recording_id=recording.id,
            format="webm"
        )

        # Convert to WAV for Whisper
        wav_path = audio_processor.convert_user_recording(webm_path, recording.id)

        # Get audio duration
        duration = audio_processor.get_audio_duration(wav_path)

        # Transcribe with Whisper
        transcription = stt_service.transcribe_audio(wav_path)

        # Analyze pronunciation
        analysis = pronunciation_service.analyze_pronunciation(
            expected_text=content.text,
            transcribed_text=transcription,
            audio_duration=duration
        )

        # Update recording with results
        recording.audio_file_path = webm_path
        recording.transcription = analysis["transcription"]
        recording.pronunciation_score = analysis["pronunciation_score"]
        recording.word_accuracy = analysis["word_accuracy"]
        recording.fluency_score = analysis["fluency_score"]
        recording.feedback_json = {
            "mistakes": analysis["mistakes"],
            "feedback": analysis["feedback"]
        }

        db.commit()
        db.refresh(recording)

        # Update user progress
        progress_service.update_progress(
            db=db,
            user_id=user_id,
            topic_id=content.topic_id,
            recording_score=recording.pronunciation_score
        )

        return recording

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing recording: {str(e)}"
        )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get recording details.
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    return recording


@router.get("/{recording_id}/audio")
async def get_recording_audio(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get user's recording audio file.
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if not os.path.exists(recording.audio_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )

    from fastapi.responses import FileResponse
    return FileResponse(
        recording.audio_file_path,
        media_type="audio/webm",
        filename=f"recording_{recording_id}.webm"
    )
