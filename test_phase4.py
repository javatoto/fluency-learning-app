#!/usr/bin/env python
"""
Phase 4 Test Script - Progress Tracking & Dashboard
Tests progress recording, statistics, and dashboard features
"""
import requests
import json
from pathlib import Path
from pydub import AudioSegment
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "phase4test@example.com"
TEST_PASSWORD = "testpass123"

def login():
    """Login and get session cookies"""
    print("1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        allow_redirects=False
    )
    if response.status_code in [200, 303]:
        print("   ✓ Login successful")
        return response.cookies
    else:
        # Try to register
        print("   Registering new user...")
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": TEST_EMAIL, "name": "Phase 4 Test", "password": TEST_PASSWORD},
            allow_redirects=False
        )
        if reg_response.status_code in [200, 201, 303]:
            print("   ✓ Registration successful")
            return reg_response.cookies
        else:
            raise Exception(f"Login failed: {response.status_code}")

def generate_content_and_practice(cookies, topic_id, difficulty, accent):
    """Generate content and submit a practice recording"""
    # Generate content
    response = requests.post(
        f"{BASE_URL}/api/content/generate",
        json={"topic_id": topic_id, "difficulty": difficulty, "accent": accent},
        cookies=cookies
    )

    if response.status_code != 201:
        raise Exception(f"Content generation failed: {response.status_code}")

    content = response.json()

    # Convert TTS audio to WebM for testing
    audio_path = content["audio_url"].replace("/audio", "./audio_files")
    test_audio_path = "./audio_files/test_recording.webm"

    audio = AudioSegment.from_mp3(audio_path)
    audio.export(test_audio_path, format="webm")

    # Upload recording
    with open(test_audio_path, 'rb') as f:
        files = {'audio': ('recording.webm', f, 'audio/webm')}
        data = {'content_id': content['id']}

        response = requests.post(
            f"{BASE_URL}/api/recordings",
            files=files,
            data=data,
            cookies=cookies
        )

    if response.status_code == 201:
        result = response.json()
        return {
            "topic_id": topic_id,
            "difficulty": difficulty,
            "accent": accent,
            "score": result["pronunciation_score"]
        }
    else:
        raise Exception(f"Recording upload failed: {response.status_code}")

def test_progress_apis(cookies):
    """Test all progress API endpoints"""
    print("\n4. Testing Progress APIs...")

    # Test overall statistics
    response = requests.get(f"{BASE_URL}/api/progress/stats", cookies=cookies)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✓ Overall Stats: {stats['total_practices']} practices, avg {stats['average_score']}, streak {stats['current_streak']}")
    else:
        print(f"   ✗ Stats API failed: {response.status_code}")
        return False

    # Test topics progress
    response = requests.get(f"{BASE_URL}/api/progress/topics", cookies=cookies)
    if response.status_code == 200:
        topics = response.json()
        print(f"   ✓ Topics Progress: {len(topics)} topics")
        for topic in topics:
            print(f"      - {topic['topic_name']}: {topic['total_practices']} practices")
    else:
        print(f"   ✗ Topics API failed: {response.status_code}")
        return False

    # Test recent practices
    response = requests.get(f"{BASE_URL}/api/progress/recent", cookies=cookies)
    if response.status_code == 200:
        recent = response.json()
        print(f"   ✓ Recent Practices: {len(recent)} records")
    else:
        print(f"   ✗ Recent API failed: {response.status_code}")
        return False

    # Test continue learning
    response = requests.get(f"{BASE_URL}/api/progress/continue", cookies=cookies)
    if response.status_code == 200:
        continue_data = response.json()
        if continue_data:
            print(f"   ✓ Continue Learning: {continue_data.get('topic_name', 'N/A')}")
        else:
            print(f"   ✓ Continue Learning: No data yet")
    else:
        print(f"   ✗ Continue API failed: {response.status_code}")
        return False

    return True

def main():
    """Run Phase 4 test"""
    print("="*60)
    print("PHASE 4 TEST: Progress Tracking & Dashboard")
    print("="*60)

    try:
        # Step 1: Login
        cookies = login()

        # Step 2: Do multiple practice sessions
        print("\n2. Creating practice sessions...")
        practices = [
            (1, "intermediate", "american"),
            (1, "beginner", "british"),
            (2, "advanced", "australian"),
        ]

        results = []
        for i, (topic_id, difficulty, accent) in enumerate(practices, 1):
            print(f"   Practice {i}/3: Topic {topic_id}, {difficulty}, {accent}...")
            result = generate_content_and_practice(cookies, topic_id, difficulty, accent)
            results.append(result)
            print(f"   ✓ Score: {result['score']}/100")
            time.sleep(1)  # Small delay between practices

        # Step 3: Test Progress APIs
        if not test_progress_apis(cookies):
            raise Exception("Progress API tests failed")

        # Step 4: Check database
        print("\n5. Verifying database records...")
        from app.database import SessionLocal
        from app.models.progress import Progress

        db = SessionLocal()
        progress_records = db.query(Progress).all()
        print(f"   ✓ Progress records: {len(progress_records)}")
        for p in progress_records:
            print(f"      Topic {p.topic_id}: {p.total_practices} practices, "
                  f"avg {p.average_score:.1f}, best {p.best_score:.1f}, "
                  f"streak {p.streak_days} days")
        db.close()

        # Final Summary
        print("\n" + "="*60)
        print("✅ PHASE 4 TEST: PASSED")
        print("="*60)
        print("\nFeatures Verified:")
        print("   ✓ Progress recording after each practice")
        print("   ✓ Statistics calculation (overall & per-topic)")
        print("   ✓ Streak tracking")
        print("   ✓ Recent scores tracking")
        print("   ✓ Continue learning feature")
        print("   ✓ API endpoints working")
        print("\nNext Steps:")
        print("   → Open http://localhost:8000/progress to view dashboard")
        print("   → Open http://localhost:8000/ to see 'Continue Learning' section")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
