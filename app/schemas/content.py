"""
Pydantic schemas for content generation and practice.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ContentGenerateRequest(BaseModel):
    """Request to generate new practice content."""
    topic_id: int
    difficulty: str  # beginner, intermediate, advanced
    accent: str  # american, british, australian


class ContentResponse(BaseModel):
    """Response containing generated content."""
    id: str
    topic_id: int
    text: str
    difficulty: str
    accent: str
    audio_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentDetail(BaseModel):
    """Detailed content information."""
    id: str
    topic_id: int
    topic_name: Optional[str] = None
    text: str
    difficulty: str
    accent: str
    audio_url: str
    created_at: datetime

    class Config:
        from_attributes = True
