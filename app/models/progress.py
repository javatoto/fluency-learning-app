"""
Progress model for tracking user learning statistics.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    total_practices = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)
    best_score = Column(Float, default=0.0, nullable=False)
    last_practiced = Column(DateTime)
    streak_days = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
        Index("idx_user_progress", "user_id"),
    )
