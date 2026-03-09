"""
Pydantic schemas for recording data.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict


class RecordingCreate(BaseModel):
    """Request to create a new recording."""
    content_id: str


class RecordingResponse(BaseModel):
    """Response containing recording analysis."""
    id: str
    user_id: str
    content_id: str
    transcription: Optional[str]
    pronunciation_score: Optional[float]
    word_accuracy: Optional[float]
    fluency_score: Optional[float]
    feedback_json: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True


class RecordingDetail(RecordingResponse):
    """Detailed recording information with content."""
    content_text: Optional[str] = None
    audio_file_path: Optional[str] = None

    class Config:
        from_attributes = True
