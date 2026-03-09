"""
Pronunciation scoring and analysis service.
"""
from typing import Dict, List
import difflib
from app.services import audio_processor


def calculate_word_accuracy(expected: str, transcribed: str) -> float:
    """
    Calculate word accuracy percentage.

    Args:
        expected: Expected text
        transcribed: Transcribed text from user

    Returns:
        Accuracy score (0-100)
    """
    expected_words = expected.lower().split()
    transcribed_words = transcribed.lower().split()

    if not expected_words:
        return 0.0

    # Use SequenceMatcher for similarity
    matcher = difflib.SequenceMatcher(None, expected_words, transcribed_words)
    similarity = matcher.ratio()

    return similarity * 100


def calculate_fluency_score(
    audio_duration: float,
    expected_text: str,
    transcribed_text: str
) -> float:
    """
    Calculate fluency score based on speaking rate and completeness.

    Args:
        audio_duration: Duration of audio in seconds
        expected_text: Expected text
        transcribed_text: Transcribed text

    Returns:
        Fluency score (0-100)
    """
    if audio_duration == 0:
        return 0.0

    # Calculate words per minute
    word_count = len(transcribed_text.split())
    wpm = (word_count / audio_duration) * 60

    # Optimal range: 150-180 WPM for English
    optimal_min = 120
    optimal_max = 200

    if optimal_min <= wpm <= optimal_max:
        rate_score = 100
    elif wpm < optimal_min:
        # Penalize slow speaking
        rate_score = (wpm / optimal_min) * 100
    else:
        # Penalize very fast speaking
        rate_score = max(0, 100 - (wpm - optimal_max) / 2)

    # Check completeness
    expected_length = len(expected_text.split())
    transcribed_length = len(transcribed_text.split())
    completeness = min(100, (transcribed_length / expected_length) * 100) if expected_length > 0 else 0

    # Weighted average
    fluency_score = (rate_score * 0.6) + (completeness * 0.4)

    return min(100, max(0, fluency_score))


def calculate_pronunciation_score(
    word_accuracy: float,
    fluency_score: float
) -> float:
    """
    Calculate overall pronunciation score.

    Args:
        word_accuracy: Word accuracy percentage
        fluency_score: Fluency score

    Returns:
        Overall pronunciation score (0-100)
    """
    # Weighted average: word accuracy is more important
    return (word_accuracy * 0.7) + (fluency_score * 0.3)


def identify_mistakes(expected: str, transcribed: str) -> List[Dict[str, str]]:
    """
    Identify specific mistakes in pronunciation.

    Args:
        expected: Expected text
        transcribed: Transcribed text

    Returns:
        List of mistakes with details
    """
    expected_words = expected.lower().split()
    transcribed_words = transcribed.lower().split()

    mistakes = []

    # Use SequenceMatcher to find differences
    matcher = difflib.SequenceMatcher(None, expected_words, transcribed_words)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            mistakes.append({
                "type": "substitution",
                "expected": " ".join(expected_words[i1:i2]),
                "actual": " ".join(transcribed_words[j1:j2]),
                "position": i1
            })
        elif tag == 'delete':
            mistakes.append({
                "type": "omission",
                "expected": " ".join(expected_words[i1:i2]),
                "actual": "",
                "position": i1
            })
        elif tag == 'insert':
            mistakes.append({
                "type": "insertion",
                "expected": "",
                "actual": " ".join(transcribed_words[j1:j2]),
                "position": i1
            })

    return mistakes


def analyze_pronunciation(
    expected_text: str,
    transcribed_text: str,
    audio_duration: float
) -> Dict:
    """
    Comprehensive pronunciation analysis.

    Args:
        expected_text: Expected text
        transcribed_text: Transcribed text from user
        audio_duration: Duration of user's audio

    Returns:
        Dictionary with scores and feedback
    """
    # Calculate scores
    word_accuracy = calculate_word_accuracy(expected_text, transcribed_text)
    fluency_score = calculate_fluency_score(audio_duration, expected_text, transcribed_text)
    overall_score = calculate_pronunciation_score(word_accuracy, fluency_score)

    # Identify mistakes
    mistakes = identify_mistakes(expected_text, transcribed_text)

    # Generate feedback message
    if overall_score >= 90:
        feedback = "Excellent pronunciation! Keep up the great work!"
    elif overall_score >= 75:
        feedback = "Good job! Minor improvements will make you sound even better."
    elif overall_score >= 60:
        feedback = "You're making progress. Focus on clarity and pacing."
    else:
        feedback = "Keep practicing! Pay attention to each word's pronunciation."

    return {
        "pronunciation_score": round(overall_score, 1),
        "word_accuracy": round(word_accuracy, 1),
        "fluency_score": round(fluency_score, 1),
        "mistakes": mistakes,
        "feedback": feedback,
        "transcription": transcribed_text
    }
