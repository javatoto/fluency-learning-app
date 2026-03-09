/**
 * Progress dashboard - charts and statistics
 */

let scoreTrendChart = null;
let topicsChart = null;

// Load all progress data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadProgressData();
});

async function loadProgressData() {
    try {
        // Load overall statistics
        let stats = null;
        const statsResponse = await fetch('/api/progress/stats');
        if (statsResponse.ok) {
            stats = await statsResponse.json();
            updateStatistics(stats);
        }

        // Load topics progress
        const topicsResponse = await fetch('/api/progress/topics');
        if (topicsResponse.ok) {
            const topics = await topicsResponse.json();
            if (topics.length > 0) {
                updateTopicsProgress(topics);
                renderTopicsChart(topics);
            } else {
                showNoProgressMessage();
            }
        }

        // Load recent scores for trend chart
        const recentResponse = await fetch('/api/progress/recent?limit=20');
        if (recentResponse.ok) {
            const recent = await recentResponse.json();
            if (recent.length > 0) {
                renderScoreTrendChart(recent);
            }
        }

        // Check for badges (use the stats variable we saved)
        if (stats) {
            checkBadges(stats);
        }

    } catch (error) {
        console.error('Error loading progress data:', error);
    }
}

function updateStatistics(stats) {
    document.getElementById('totalPractices').textContent = stats.total_practices || 0;
    document.getElementById('averageScore').textContent = stats.average_score || 0;
    document.getElementById('bestScore').textContent = stats.best_score || 0;
    document.getElementById('currentStreak').textContent = stats.current_streak || 0;
}

function updateTopicsProgress(topics) {
    const container = document.getElementById('topicsProgress');
    container.innerHTML = '';

    topics.forEach(topic => {
        const topicDiv = document.createElement('div');
        topicDiv.className = 'border-b pb-4 last:border-b-0';
        topicDiv.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center">
                    <span class="text-2xl mr-3">${topic.topic_icon}</span>
                    <div>
                        <h3 class="font-semibold text-gray-900">${topic.topic_name}</h3>
                        <p class="text-sm text-gray-500">${topic.total_practices} practice${topic.total_practices !== 1 ? 's' : ''}</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-lg font-bold text-indigo-600">${topic.average_score}/100</div>
                    <div class="text-xs text-gray-500">Best: ${topic.best_score}</div>
                </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                     style="width: ${topic.average_score}%"></div>
            </div>
            ${topic.streak_days > 0 ? `
                <div class="mt-2 text-xs text-orange-600">
                    🔥 ${topic.streak_days} day streak!
                </div>
            ` : ''}
        `;
        container.appendChild(topicDiv);
    });
}

function renderScoreTrendChart(recentScores) {
    const ctx = document.getElementById('scoreTrendChart');

    // Reverse to show oldest to newest
    const scores = recentScores.reverse();

    const labels = scores.map((_, index) => `Practice ${index + 1}`);
    const data = scores.map(s => s.score);

    if (scoreTrendChart) {
        scoreTrendChart.destroy();
    }

    scoreTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pronunciation Score',
                data: data,
                borderColor: 'rgb(79, 70, 229)',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.3,
                fill: true,
                pointBackgroundColor: 'rgb(79, 70, 229)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.parsed.y}/100`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value;
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function renderTopicsChart(topics) {
    const ctx = document.getElementById('topicsChart');

    // Take top 6 topics by practice count
    const topTopics = topics.slice(0, 6);

    const labels = topTopics.map(t => t.topic_name);
    const data = topTopics.map(t => t.average_score);
    const colors = [
        'rgba(79, 70, 229, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)'
    ];

    if (topicsChart) {
        topicsChart.destroy();
    }

    topicsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Score',
                data: data,
                backgroundColor: colors.slice(0, topTopics.length),
                borderColor: colors.slice(0, topTopics.length).map(c => c.replace('0.8', '1')),
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Average: ${context.parsed.y}/100`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function checkBadges(stats) {
    if (!stats) return;

    const badgesContainer = document.getElementById('badgesContainer');
    const badgesSection = document.getElementById('badgesSection');
    const badges = [];

    // Streak badges
    if (stats.current_streak >= 3) {
        badges.push({ icon: '🥉', title: '3-Day Streak', description: 'Practiced 3 days in a row' });
    }
    if (stats.current_streak >= 7) {
        badges.push({ icon: '🥈', title: '7-Day Streak', description: 'Practiced 7 days in a row' });
    }
    if (stats.current_streak >= 30) {
        badges.push({ icon: '🥇', title: '30-Day Streak', description: 'Practiced 30 days in a row' });
    }

    // Practice count badges
    if (stats.total_practices >= 10) {
        badges.push({ icon: '⭐', title: 'Getting Started', description: 'Completed 10 practices' });
    }
    if (stats.total_practices >= 50) {
        badges.push({ icon: '🌟', title: 'Dedicated Learner', description: 'Completed 50 practices' });
    }
    if (stats.total_practices >= 100) {
        badges.push({ icon: '💫', title: 'Master Practitioner', description: 'Completed 100 practices' });
    }

    // Score badges
    if (stats.best_score >= 90) {
        badges.push({ icon: '🏆', title: 'Excellence', description: 'Scored 90+ on a practice' });
    }
    if (stats.average_score >= 80) {
        badges.push({ icon: '🎯', title: 'Consistent Quality', description: 'Average score above 80' });
    }

    if (badges.length > 0) {
        badgesSection.classList.remove('hidden');
        badgesContainer.innerHTML = badges.map(badge => `
            <div class="flex flex-col items-center p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg border-2 border-yellow-300">
                <span class="text-4xl mb-2">${badge.icon}</span>
                <h3 class="font-semibold text-gray-900 text-sm">${badge.title}</h3>
                <p class="text-xs text-gray-600 text-center mt-1">${badge.description}</p>
            </div>
        `).join('');
    }
}

function showNoProgressMessage() {
    document.getElementById('noProgressMessage').classList.remove('hidden');
    document.getElementById('topicsProgress').classList.add('hidden');
}
