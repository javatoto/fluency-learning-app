/**
 * Practice page functionality - audio recording and content generation
 */

let currentContent = null;
let mediaRecorder = null;
let audioChunks = [];
let recordedBlob = null;

// DOM elements
const generateBtn = document.getElementById('generateBtn');
const practiceContent = document.getElementById('practiceContent');
const loadingSpinner = document.getElementById('loadingSpinner');
const practiceText = document.getElementById('practiceText');
const nativeAudio = document.getElementById('nativeAudio');
const recordBtn = document.getElementById('recordBtn');
const recordingStatus = document.getElementById('recordingStatus');
const userAudioContainer = document.getElementById('userAudioContainer');
const userAudio = document.getElementById('userAudio');
const submitBtn = document.getElementById('submitBtn');
const feedbackSection = document.getElementById('feedbackSection');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const difficultySelect = document.getElementById('difficultySelect');
const accentSelect = document.getElementById('accentSelect');

// Get topic ID from URL
const urlParams = new URLSearchParams(window.location.search);
const topicId = urlParams.get('topic');

if (!topicId) {
    window.location.href = '/';
}

// Generate new practice content
generateBtn.addEventListener('click', async () => {
    const difficulty = difficultySelect.value;
    const accent = accentSelect.value;

    // Show loading
    loadingSpinner.classList.remove('hidden');
    practiceContent.classList.add('hidden');
    feedbackSection.classList.add('hidden');

    try {
        const response = await fetch('/api/content/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic_id: parseInt(topicId),
                difficulty: difficulty,
                accent: accent
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate content');
        }

        currentContent = await response.json();

        // Display content
        practiceText.textContent = currentContent.text;
        nativeAudio.src = currentContent.audio_url;

        // Reset recording state
        resetRecordingState();

        // Show practice content
        loadingSpinner.classList.add('hidden');
        practiceContent.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        alert('Error generating content: ' + error.message);
        loadingSpinner.classList.add('hidden');
    }
});

// Recording functionality
recordBtn.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        // Stop recording
        mediaRecorder.stop();
        recordBtn.textContent = '⏺';
        recordBtn.classList.remove('recording');
        recordBtn.classList.replace('bg-gray-500', 'bg-red-500');
        recordingStatus.textContent = 'Processing recording...';
    } else {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioURL = URL.createObjectURL(recordedBlob);
                userAudio.src = audioURL;
                userAudioContainer.classList.remove('hidden');
                submitBtn.classList.remove('hidden');
                recordingStatus.textContent = 'Recording saved! Review and submit for feedback.';

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            recordBtn.textContent = '⏹';
            recordBtn.classList.add('recording');
            recordBtn.classList.replace('bg-red-500', 'bg-gray-500');
            recordingStatus.innerHTML = '<div class="waveform"><span></span><span></span><span></span><span></span><span></span></div>';

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please ensure you have granted microphone permissions.');
        }
    }
});

// Submit recording for analysis
submitBtn.addEventListener('click', async () => {
    if (!recordedBlob || !currentContent) {
        return;
    }

    // Show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';

    try {
        const formData = new FormData();
        formData.append('audio', recordedBlob, 'recording.webm');
        formData.append('content_id', currentContent.id);

        const response = await fetch('/api/recordings', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to analyze recording');
        }

        const result = await response.json();

        // Display feedback
        displayFeedback(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing recording: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Pronunciation Feedback';
    }
});

// Display feedback results
function displayFeedback(result) {
    // Update score badges
    updateScoreBadge('scoreOverall', result.pronunciation_score);
    updateScoreBadge('scoreAccuracy', result.word_accuracy);
    updateScoreBadge('scoreFluency', result.fluency_score);

    // Display transcription
    document.getElementById('transcriptionText').textContent = result.transcription || 'No transcription available';

    // Show feedback section
    feedbackSection.classList.remove('hidden');
}

// Update score badge
function updateScoreBadge(elementId, score) {
    const badge = document.getElementById(elementId);
    badge.textContent = Math.round(score);

    // Remove existing score classes
    badge.classList.remove('score-excellent', 'score-good', 'score-fair', 'score-poor');

    // Add appropriate class based on score
    if (score >= 90) {
        badge.classList.add('score-excellent');
    } else if (score >= 75) {
        badge.classList.add('score-good');
    } else if (score >= 60) {
        badge.classList.add('score-fair');
    } else {
        badge.classList.add('score-poor');
    }
}

// Reset recording state
function resetRecordingState() {
    recordedBlob = null;
    audioChunks = [];
    userAudioContainer.classList.add('hidden');
    submitBtn.classList.add('hidden');
    feedbackSection.classList.add('hidden');
    recordingStatus.textContent = 'Click to start recording';
    recordBtn.textContent = '⏺';
    recordBtn.classList.remove('recording');
    recordBtn.classList.replace('bg-gray-500', 'bg-red-500');
}

// Try again button
tryAgainBtn.addEventListener('click', () => {
    resetRecordingState();
    feedbackSection.classList.add('hidden');
});

// Auto-generate content on page load
window.addEventListener('load', () => {
    generateBtn.click();
});
