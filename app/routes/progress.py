"""
Progress tracking and statistics routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import progress_service
from app.routes.auth import get_current_user_dependency
from app.models.user import User
from typing import Dict, List

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/stats")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
) -> Dict:
    """
    Get overall statistics for the current user.

    Returns:
        Dictionary with aggregated stats across all topics
    """
    stats = progress_service.get_user_statistics(db, current_user.id)
    return stats


@router.get("/topics")
async def get_all_topics_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
) -> List[Dict]:
    """
    Get progress for all topics practiced by the user.

    Returns:
        List of progress records for each topic
    """
    progress = progress_service.get_all_topic_progress(db, current_user.id)
    return progress


@router.get("/topics/{topic_id}")
async def get_topic_progress(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
) -> Dict:
    """
    Get detailed progress for a specific topic.

    Args:
        topic_id: Topic ID

    Returns:
        Progress statistics for the topic
    """
    progress = progress_service.get_topic_progress(db, current_user.id, topic_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this topic"
        )

    return progress


@router.get("/recent")
async def get_recent_practices(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
) -> List[Dict]:
    """
    Get recent practice sessions with scores.

    Args:
        limit: Number of recent practices to return (default: 10)

    Returns:
        List of recent recordings with scores
    """
    recent = progress_service.get_recent_scores(db, current_user.id, limit)
    return recent


@router.get("/continue")
async def get_continue_learning(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
) -> Dict:
    """
    Get information about the last practiced topic for "Continue Learning" feature.

    Returns:
        Last practiced topic info or empty dict
    """
    last_topic = progress_service.get_last_practiced_topic(db, current_user.id)

    if not last_topic:
        return {}

    return last_topic
