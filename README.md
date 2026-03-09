# 🗣️ Fluency Learning App

An AI-powered English pronunciation learning platform that helps users master business English through interactive practice with instant feedback.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎯 AI-Powered Learning
- **Smart Content Generation**: GPT-4 generates contextual business English sentences
- **Native Audio**: Text-to-speech with multiple accents (American, British, Australian)
- **Pronunciation Analysis**: OpenAI Whisper for accurate speech-to-text transcription
- **Intelligent Scoring**: Advanced algorithms analyze word accuracy, fluency, and pronunciation

### 📊 Progress Tracking
- **Dashboard**: Visual charts showing improvement over time
- **Statistics**: Track total practices, average scores, and personal bests
- **Streak System**: Maintain daily practice streaks
- **Badges & Achievements**: Earn rewards for milestones (3-day, 7-day, 30-day streaks)

### 🎓 Personalized Experience
- **Multiple Difficulty Levels**: Beginner, Intermediate, Advanced
- **Topic-Based Learning**: Business meetings, emails, presentations, negotiations, and more
- **Continue Learning**: Resume where you left off
- **Detailed Feedback**: Get specific mistakes identified and corrective suggestions

### 📱 User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Recording**: Browser-based audio recording with instant feedback
- **Progress Visualization**: Interactive charts powered by Chart.js
- **Modern UI**: Clean, intuitive interface built with Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- FFmpeg (for audio processing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fluency-learning-app.git
cd fluency-learning-app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install FFmpeg** (required for audio processing)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Example `.env` file:
```env
# Application
SECRET_KEY=your-secret-key-here-generate-random-string
DEBUG=True

# Database
DATABASE_URL=sqlite:///./fluency.db

# OpenAI
OPENAI_API_KEY=sk-proj-your-api-key-here

# Audio Settings
MAX_RECORDING_DURATION=60
MAX_FILE_SIZE_MB=5
AUDIO_STORAGE_PATH=./audio_files
```

6. **Initialize the database**
```bash
alembic upgrade head
```

7. **Seed the database with topics**
```bash
python -m app.scripts.seed_topics
```

8. **Run the application**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

9. **Open in browser**
```
http://localhost:8000
```

## 📖 Usage Guide

### Getting Started

1. **Register an account** at `/register`
2. **Login** at `/login`
3. **Choose a topic** from the home page
4. **Select difficulty and accent** on the practice page
5. **Generate practice content** with the AI
6. **Listen to native audio** and practice pronunciation
7. **Record yourself** speaking the same phrase
8. **Get instant feedback** with detailed scores and suggestions
9. **Track your progress** on the dashboard

### Practice Flow

```
Home → Select Topic → Configure Settings → Generate Content
  ↓
Listen to Native Audio → Record Your Voice → Submit
  ↓
View Results (Score, Accuracy, Fluency) → Try Again or New Topic
  ↓
Progress Dashboard (Charts, Stats, Badges)
```

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database management
- Alembic - Database migrations
- Pydantic - Data validation

**AI/ML:**
- OpenAI GPT-4 - Content generation
- OpenAI TTS - Text-to-speech conversion
- OpenAI Whisper - Speech-to-text transcription
- Custom scoring algorithms - Pronunciation analysis

**Frontend:**
- Jinja2 Templates - Server-side rendering
- Tailwind CSS - Utility-first styling
- Chart.js - Data visualization
- Vanilla JavaScript - Client-side logic

**Audio:**
- pydub - Audio processing
- MediaRecorder API - Browser recording
- FFmpeg - Audio conversion

### Project Structure

```
fluency-learning-app/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API and page routes
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic schemas
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # Application entry
├── alembic/             # Database migrations
├── audio_files/         # Audio storage
│   ├── tts/            # Generated TTS audio
│   └── recordings/     # User recordings
├── tests/              # Test files
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## 🧪 Testing

### Run Phase Tests

```bash
# Phase 2: Content Generation & Audio
python test_phase2.py

# Phase 3: Recording & Pronunciation Analysis
python test_phase3.py
python test_phase3_mistakes.py

# Phase 4: Progress Tracking
python test_phase4.py
```

### Manual Testing

1. Test content generation with different difficulties and accents
2. Test recording functionality on different browsers
3. Verify progress tracking after multiple sessions
4. Check dashboard charts and statistics
5. Test "Continue Learning" feature

## 🔧 Configuration

### OpenAI API Setup

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env` file: `OPENAI_API_KEY=sk-proj-your-key`
3. Ensure you have credits in your OpenAI account

### SSL Certificate Issues (Corporate Proxy)

If you're behind a corporate proxy with SSL inspection, the OpenAI client has been configured to disable SSL verification for development. For production, configure proper SSL certificates.

### Database Configuration

Default is SQLite for development. For production, update `DATABASE_URL` in `.env`:

```env
# PostgreSQL example
DATABASE_URL=postgresql://user:password@localhost/fluency_db
```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

**Content:**
- `POST /api/content/generate` - Generate practice content
- `GET /api/content/{id}` - Get content by ID
- `GET /api/content/{id}/audio` - Get audio file

**Recordings:**
- `POST /api/recordings` - Upload and analyze recording
- `GET /api/recordings/{id}` - Get recording details
- `GET /api/recordings/{id}/audio` - Get recording audio

**Progress:**
- `GET /api/progress/stats` - Get overall statistics
- `GET /api/progress/topics` - Get all topics progress
- `GET /api/progress/recent` - Get recent practice sessions
- `GET /api/progress/continue` - Get last practiced topic

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate secure `SECRET_KEY`
- [ ] Use production database (PostgreSQL recommended)
- [ ] Configure proper SSL certificates
- [ ] Set up proper logging
- [ ] Configure CORS appropriately
- [ ] Set up backup for audio files
- [ ] Monitor OpenAI API usage and costs
- [ ] Implement rate limiting
- [ ] Set up error monitoring (e.g., Sentry)

### Deploy to Cloud

Example using Docker:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations
RUN alembic upgrade head

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4, Whisper, and TTS APIs
- FastAPI for the excellent web framework
- Chart.js for beautiful visualizations
- Tailwind CSS for styling utilities

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Contact: support@fluencyapp.com (example)

## 🗺️ Roadmap

### Completed ✅
- [x] User authentication and authorization
- [x] AI content generation with GPT-4
- [x] Multi-accent TTS (American, British, Australian)
- [x] Voice recording and transcription
- [x] Pronunciation scoring and feedback
- [x] Progress tracking and statistics
- [x] Dashboard with charts
- [x] Streak system and badges
- [x] Continue learning feature

### Future Features 🚀
- [ ] Mobile app (iOS/Android)
- [ ] More languages support
- [ ] Conversation practice (multi-turn dialogues)
- [ ] Peer comparison and leaderboards
- [ ] Custom vocabulary lists
- [ ] Offline practice mode
- [ ] Speech pattern analysis
- [ ] Video pronunciation guides
- [ ] Gamification enhancements
- [ ] Social features (share progress)

---

**Built with ❤️ using Claude Code**

*Helping people speak English with confidence!* 🎯
