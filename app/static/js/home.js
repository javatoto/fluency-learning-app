/**
 * Home page functionality - Continue Learning feature
 */

document.addEventListener('DOMContentLoaded', async () => {
    await loadContinueLearning();
});

async function loadContinueLearning() {
    try {
        const response = await fetch('/api/progress/continue');
        if (response.ok) {
            const data = await response.json();

            if (data && data.topic_id) {
                showContinueLearning(data);
            }
        }
    } catch (error) {
        console.error('Error loading continue learning:', error);
    }
}

function showContinueLearning(data) {
    const section = document.getElementById('continueLearningSection');
    const icon = document.getElementById('continueTopicIcon');
    const name = document.getElementById('continueTopicName');
    const timestamp = document.getElementById('continueTimestamp');
    const avgScore = document.getElementById('continueAvgScore');
    const button = document.getElementById('continueButton');

    icon.textContent = data.topic_icon;
    name.textContent = data.topic_name;
    avgScore.textContent = data.average_score;

    // Format timestamp
    const date = new Date(data.last_practiced);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    let timeText;
    if (diffMins < 1) {
        timeText = 'just now';
    } else if (diffMins < 60) {
        timeText = `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        timeText = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays === 1) {
        timeText = 'yesterday';
    } else {
        timeText = `${diffDays} days ago`;
    }

    timestamp.textContent = timeText;

    // Set button link
    button.href = `/practice?topic=${data.topic_id}`;

    // Show section
    section.classList.remove('hidden');
}
