"""
Progress tracking service for managing user learning statistics.
"""
from sqlalchemy.orm import Session
from app.models.progress import Progress
from app.models.recording import Recording
from app.models.user import User
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def update_progress(
    db: Session,
    user_id: str,
    topic_id: int,
    recording_score: float
) -> Progress:
    """
    Update user progress after completing a practice session.

    Args:
        db: Database session
        user_id: User ID
        topic_id: Topic ID
        recording_score: Pronunciation score from the recording (0-100)

    Returns:
        Updated Progress record
    """
    # Get or create progress record for this user-topic combination
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.topic_id == topic_id
    ).first()

    if not progress:
        # Create new progress record
        progress = Progress(
            user_id=user_id,
            topic_id=topic_id,
            total_practices=0,
            average_score=0.0,
            best_score=0.0,
            streak_days=0
        )
        db.add(progress)

    # Update statistics
    progress.total_practices += 1

    # Calculate new average score
    # (old_avg * old_count + new_score) / new_count
    old_total = progress.average_score * (progress.total_practices - 1)
    progress.average_score = (old_total + recording_score) / progress.total_practices

    # Update best score
    if recording_score > progress.best_score:
        progress.best_score = recording_score

    # Update streak
    today = datetime.utcnow().date()
    if progress.last_practiced:
        last_practice_date = progress.last_practiced.date()
        days_diff = (today - last_practice_date).days

        if days_diff == 0:
            # Same day - no change to streak
            pass
        elif days_diff == 1:
            # Consecutive day - increment streak
            progress.streak_days += 1
        else:
            # Streak broken - reset to 1
            progress.streak_days = 1
    else:
        # First practice - start streak
        progress.streak_days = 1

    # Update last practiced timestamp
    progress.last_practiced = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    return progress


def get_user_statistics(db: Session, user_id: str) -> Dict:
    """
    Get overall statistics for a user across all topics.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with overall stats
    """
    # Get all progress records for user
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).all()

    if not progress_records:
        return {
            "total_practices": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "topics_practiced": 0,
            "current_streak": 0,
            "longest_streak": 0
        }

    # Calculate aggregated statistics
    total_practices = sum(p.total_practices for p in progress_records)

    # Weighted average across all topics
    if total_practices > 0:
        weighted_avg = sum(
            p.average_score * p.total_practices for p in progress_records
        ) / total_practices
    else:
        weighted_avg = 0.0

    best_score = max(p.best_score for p in progress_records)
    topics_practiced = len(progress_records)

    # Current streak is the maximum streak across all topics
    # (assumes user practices at least one topic daily to maintain streak)
    current_streak = max(p.streak_days for p in progress_records)

    return {
        "total_practices": total_practices,
        "average_score": round(weighted_avg, 1),
        "best_score": round(best_score, 1),
        "topics_practiced": topics_practiced,
        "current_streak": current_streak,
        "longest_streak": current_streak  # For now, same as current
    }


def get_topic_progress(db: Session, user_id: str, topic_id: int) -> Optional[Dict]:
    """
    Get detailed progress for a specific topic.

    Args:
        db: Database session
        user_id: User ID
        topic_id: Topic ID

    Returns:
        Dictionary with topic-specific stats or None
    """
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.topic_id == topic_id
    ).first()

    if not progress:
        return None

    return {
        "topic_id": topic_id,
        "total_practices": progress.total_practices,
        "average_score": round(progress.average_score, 1),
        "best_score": round(progress.best_score, 1),
        "last_practiced": progress.last_practiced.isoformat() if progress.last_practiced else None,
        "streak_days": progress.streak_days
    }


def get_all_topic_progress(db: Session, user_id: str) -> List[Dict]:
    """
    Get progress for all topics practiced by user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of progress dictionaries for each topic
    """
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).all()

    result = []
    for progress in progress_records:
        result.append({
            "topic_id": progress.topic_id,
            "topic_name": progress.topic.name if progress.topic else "Unknown",
            "topic_icon": progress.topic.icon if progress.topic else "",
            "total_practices": progress.total_practices,
            "average_score": round(progress.average_score, 1),
            "best_score": round(progress.best_score, 1),
            "last_practiced": progress.last_practiced.isoformat() if progress.last_practiced else None,
            "streak_days": progress.streak_days
        })

    # Sort by last practiced (most recent first)
    result.sort(key=lambda x: x["last_practiced"] or "", reverse=True)

    return result


def get_recent_scores(db: Session, user_id: str, limit: int = 10) -> List[Dict]:
    """
    Get recent practice scores for a user.

    Args:
        db: Database session
        user_id: User ID
        limit: Number of recent scores to return

    Returns:
        List of recent recordings with scores
    """
    recordings = db.query(Recording).filter(
        Recording.user_id == user_id,
        Recording.pronunciation_score.isnot(None)
    ).order_by(
        Recording.created_at.desc()
    ).limit(limit).all()

    result = []
    for recording in recordings:
        result.append({
            "date": recording.created_at.isoformat(),
            "topic_id": recording.content.topic_id if recording.content else None,
            "topic_name": recording.content.topic.name if recording.content and recording.content.topic else "Unknown",
            "score": round(recording.pronunciation_score, 1),
            "word_accuracy": round(recording.word_accuracy, 1) if recording.word_accuracy else 0,
            "fluency_score": round(recording.fluency_score, 1) if recording.fluency_score else 0
        })

    return result


def get_last_practiced_topic(db: Session, user_id: str) -> Optional[Dict]:
    """
    Get the most recently practiced topic for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with last practiced topic info or None
    """
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.last_practiced.isnot(None)
    ).order_by(
        Progress.last_practiced.desc()
    ).first()

    if not progress:
        return None

    return {
        "topic_id": progress.topic_id,
        "topic_name": progress.topic.name if progress.topic else "Unknown",
        "topic_icon": progress.topic.icon if progress.topic else "",
        "last_practiced": progress.last_practiced.isoformat(),
        "average_score": round(progress.average_score, 1)
    }
