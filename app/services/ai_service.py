"""
AI service for generating practice content using OpenAI GPT-4.
"""
from openai import OpenAI
from app.config import settings
from typing import List, Dict
import httpx

# Initialize OpenAI client with SSL verification disabled for development
# This is needed when behind corporate proxies with SSL inspection
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.Client(verify=False)
)


def generate_practice_content(
    topic: str,
    difficulty: str,
    num_sentences: int = 3
) -> List[str]:
    """
    Generate practice sentences for a given topic and difficulty level.

    Args:
        topic: The topic name (e.g., "Business Meetings")
        difficulty: Difficulty level (beginner, intermediate, advanced)
        num_sentences: Number of sentences to generate

    Returns:
        List of practice sentences
    """
    # Define prompts based on difficulty
    difficulty_context = {
        "beginner": "Use simple vocabulary and short sentences (8-12 words). Focus on basic phrases.",
        "intermediate": "Use moderate vocabulary and medium-length sentences (12-18 words). Include some business terminology.",
        "advanced": "Use sophisticated vocabulary and complex sentences (15-25 words). Include idiomatic expressions and advanced business terminology."
    }

    system_prompt = f"""You are an expert English language teacher specializing in business English pronunciation practice.
Generate clear, natural-sounding sentences for pronunciation practice.
Topic: {topic}
Difficulty: {difficulty}
{difficulty_context.get(difficulty, difficulty_context['intermediate'])}

Requirements:
- Each sentence should be complete and grammatically correct
- Sentences should sound natural when spoken aloud
- Focus on practical, real-world usage
- Vary sentence structure and vocabulary
- Make sentences engaging and relevant to {topic}
"""

    user_prompt = f"Generate {num_sentences} practice sentences for pronunciation practice on the topic of '{topic}' at {difficulty} level. Return only the sentences, one per line, without numbering or additional formatting."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )

        # Extract sentences from response
        content = response.choices[0].message.content.strip()
        sentences = [s.strip() for s in content.split('\n') if s.strip()]

        # Remove any numbering if present
        sentences = [s.lstrip('0123456789.- ') for s in sentences]

        return sentences[:num_sentences]

    except Exception as e:
        raise Exception(f"Error generating content: {str(e)}")


def generate_single_sentence(topic: str, difficulty: str) -> str:
    """
    Generate a single practice sentence.

    Args:
        topic: The topic name
        difficulty: Difficulty level

    Returns:
        A single practice sentence
    """
    sentences = generate_practice_content(topic, difficulty, num_sentences=1)
    return sentences[0] if sentences else ""


def generate_conversation_exchange(
    topic: str,
    difficulty: str,
    num_exchanges: int = 2
) -> List[Dict[str, str]]:
    """
    Generate a conversation exchange for practice.

    Args:
        topic: The topic name
        difficulty: Difficulty level
        num_exchanges: Number of conversation exchanges

    Returns:
        List of conversation exchanges with speaker and text
    """
    difficulty_context = {
        "beginner": "simple and direct",
        "intermediate": "natural and professional",
        "advanced": "sophisticated and nuanced"
    }

    system_prompt = f"""You are an expert English language teacher creating conversation practice materials.
Generate a realistic {difficulty_context.get(difficulty, 'natural')} business conversation for the topic: {topic}

Format each line as:
Speaker A: [text]
Speaker B: [text]

Make the conversation natural and appropriate for {difficulty} level learners."""

    user_prompt = f"Generate a {num_exchanges}-exchange conversation about {topic}. Keep it practical and relevant to business scenarios."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=400
        )

        content = response.choices[0].message.content.strip()
        lines = content.split('\n')

        exchanges = []
        for line in lines:
            if ':' in line:
                speaker, text = line.split(':', 1)
                exchanges.append({
                    "speaker": speaker.strip(),
                    "text": text.strip()
                })

        return exchanges[:num_exchanges * 2]  # 2 lines per exchange

    except Exception as e:
        raise Exception(f"Error generating conversation: {str(e)}")
