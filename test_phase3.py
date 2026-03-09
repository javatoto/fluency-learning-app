#!/usr/bin/env python
"""
Phase 3 Test Script - Recording & Pronunciation Analysis
Tests the full flow: audio upload → transcription → scoring → feedback
"""
import requests
import json
from pathlib import Path
from pydub import AudioSegment

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "phase3test@example.com"
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
        print(f"   ✗ Login failed: {response.status_code}")
        # Try to register
        print("   Attempting to register...")
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": TEST_EMAIL, "name": "Test User", "password": TEST_PASSWORD},
            allow_redirects=False
        )
        if reg_response.status_code in [200, 201, 303]:
            print("   ✓ Registration successful")
            return reg_response.cookies
        else:
            raise Exception(f"Registration failed: {reg_response.status_code} - {reg_response.text}")

def get_content():
    """Get existing content for testing"""
    print("\n2. Getting test content...")
    from app.database import SessionLocal
    from app.models.content import Content

    db = SessionLocal()
    content = db.query(Content).first()
    db.close()

    if content:
        print(f"   ✓ Content ID: {content.id}")
        print(f"   ✓ Text: {content.text[:60]}...")
        return content
    else:
        raise Exception("No content found. Run Phase 2 test first.")

def prepare_test_audio(content):
    """Convert TTS audio to WebM for testing"""
    print("\n3. Preparing test audio...")

    # Get the TTS audio file
    audio_path = content.audio_url.replace("/audio", "./audio_files")

    if not Path(audio_path).exists():
        raise Exception(f"Audio file not found: {audio_path}")

    # Convert MP3 to WebM (simulating browser recording)
    test_audio_path = "./audio_files/test_recording.webm"
    audio = AudioSegment.from_mp3(audio_path)
    audio.export(test_audio_path, format="webm")

    print(f"   ✓ Test audio created: {test_audio_path}")
    return test_audio_path

def test_recording_upload(content_id, audio_path, cookies):
    """Test the recording upload and analysis"""
    print("\n4. Uploading recording for analysis...")

    with open(audio_path, 'rb') as f:
        files = {'audio': ('recording.webm', f, 'audio/webm')}
        data = {'content_id': content_id}

        response = requests.post(
            f"{BASE_URL}/api/recordings",
            files=files,
            data=data,
            cookies=cookies
        )

    if response.status_code == 201:
        print("   ✓ Recording uploaded successfully")
        result = response.json()
        return result
    else:
        print(f"   ✗ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def display_results(result):
    """Display pronunciation analysis results"""
    if not result:
        return

    print("\n" + "="*60)
    print("PHASE 3 TEST RESULTS - PRONUNCIATION ANALYSIS")
    print("="*60)

    print(f"\n📝 Transcription:")
    print(f"   {result['transcription']}")

    print(f"\n📊 Scores:")
    print(f"   Overall:       {result['pronunciation_score']}/100")
    print(f"   Word Accuracy: {result['word_accuracy']}/100")
    print(f"   Fluency:       {result['fluency_score']}/100")

    print(f"\n💬 Feedback:")
    print(f"   {result['feedback_json']['feedback']}")

    if result['feedback_json']['mistakes']:
        print(f"\n⚠️  Mistakes Found: {len(result['feedback_json']['mistakes'])}")
        for i, mistake in enumerate(result['feedback_json']['mistakes'][:3], 1):
            print(f"   {i}. {mistake['type']}: '{mistake['expected']}' → '{mistake['actual']}'")
    else:
        print("\n✅ No mistakes detected!")

    print("\n" + "="*60)

    # Determine if test passed
    if result['pronunciation_score'] >= 80:
        print("✅ PHASE 3 TEST: PASSED")
        print("   Recording, transcription, and scoring all working correctly!")
    elif result['pronunciation_score'] >= 60:
        print("⚠️  PHASE 3 TEST: PARTIAL")
        print("   System is working but scores need verification")
    else:
        print("❌ PHASE 3 TEST: NEEDS REVIEW")
        print("   Scores seem low for TTS-generated audio")

    print("="*60)

def main():
    """Run Phase 3 test"""
    print("="*60)
    print("PHASE 3 TEST: Recording & Pronunciation Analysis")
    print("="*60)

    try:
        # Step 1: Login
        cookies = login()

        # Step 2: Get content
        content = get_content()

        # Step 3: Prepare test audio
        audio_path = prepare_test_audio(content)

        # Step 4: Upload and analyze
        result = test_recording_upload(content.id, audio_path, cookies)

        # Step 5: Display results
        display_results(result)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
