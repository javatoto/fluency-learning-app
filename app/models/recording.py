"""
Recording model for user pronunciation practice sessions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("contents.id"), nullable=False, index=True)
    audio_file_path = Column(String, nullable=True)  # Allow null initially, set after upload
    transcription = Column(Text)
    pronunciation_score = Column(Float)  # 0-100
    word_accuracy = Column(Float)  # 0-100
    fluency_score = Column(Float)  # 0-100
    feedback_json = Column(JSON)  # detailed mistake analysis
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="recordings")
    content = relationship("Content", back_populates="recordings")
