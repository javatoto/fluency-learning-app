"""
Content model for practice sentences/paragraphs with audio.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AccentType(str, enum.Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"


class Content(Base):
    __tablename__ = "contents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    text = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    accent = Column(Enum(AccentType), nullable=False)
    audio_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="contents")
    recordings = relationship("Recording", back_populates="content", cascade="all, delete-orphan")

    # Index for quick lookups
    __table_args__ = (
        Index("idx_topic_difficulty_accent", "topic_id", "difficulty", "accent"),
    )
