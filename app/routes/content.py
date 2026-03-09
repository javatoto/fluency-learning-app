"""
Content generation and retrieval routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.content import ContentGenerateRequest, ContentResponse
from app.models.content import Content, DifficultyLevel, AccentType
from app.models.topic import Topic
from app.services import ai_service, tts_service
import os

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/generate", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def generate_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate new practice content with AI and TTS.

    This endpoint:
    1. Checks if content already exists for this combination
    2. Generates text using GPT-4
    3. Generates audio using OpenAI TTS
    4. Saves to database
    """
    # Validate topic exists
    topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    # Validate difficulty and accent
    try:
        difficulty = DifficultyLevel(request.difficulty.lower())
        accent = AccentType(request.accent.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid difficulty or accent"
        )

    # Check if content already exists (for caching)
    existing_content = db.query(Content).filter(
        Content.topic_id == request.topic_id,
        Content.difficulty == difficulty,
        Content.accent == accent
    ).first()

    if existing_content:
        return existing_content

    try:
        # Generate text content using AI
        text = ai_service.generate_single_sentence(
            topic=topic.name,
            difficulty=request.difficulty
        )

        # Create content record (to get ID)
        content = Content(
            topic_id=request.topic_id,
            text=text,
            difficulty=difficulty,
            accent=accent,
            audio_url=""  # Will be updated after TTS
        )
        db.add(content)
        db.flush()  # Get the ID without committing

        # Generate audio using TTS
        audio_path = tts_service.generate_speech_for_content(
            content_id=content.id,
            text=text,
            accent=request.accent
        )

        # Update content with audio URL
        content.audio_url = audio_path
        db.commit()
        db.refresh(content)

        return content

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str, db: Session = Depends(get_db)):
    """
    Get specific content by ID.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.get("/{content_id}/audio")
async def get_content_audio(content_id: str, db: Session = Depends(get_db)):
    """
    Stream audio file for specific content.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Convert URL path to filesystem path
    # /audio/tts/american/xxx.mp3 -> ./audio_files/tts/american/xxx.mp3
    audio_path = content.audio_url.replace("/audio", "./audio_files")

    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"content_{content_id}.mp3"
    )
