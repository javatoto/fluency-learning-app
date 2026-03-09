"""
Seed script to populate database with initial business topics.
"""
from app.database import SessionLocal, engine
from app.models.topic import Topic
from app.database import Base


def seed_topics():
    """Seed the database with business topics."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if topics already exist
        existing_topics = db.query(Topic).count()
        if existing_topics > 0:
            print(f"Topics already exist ({existing_topics} topics found). Skipping seed.")
            return

        # Define business topics
        topics = [
            {
                "name": "Business Meetings",
                "description": "Practice common phrases and expressions used in professional meetings, presentations, and discussions.",
                "category": "Business",
                "icon": "💼"
            },
            {
                "name": "Professional Emails",
                "description": "Learn to articulate email phrases clearly, including greetings, requests, and professional closings.",
                "category": "Business",
                "icon": "📧"
            },
            {
                "name": "Presentations",
                "description": "Master the pronunciation of key presentation phrases, from opening statements to Q&A sessions.",
                "category": "Business",
                "icon": "📊"
            },
            {
                "name": "Negotiations",
                "description": "Practice speaking confidently during business negotiations, deals, and contract discussions.",
                "category": "Business",
                "icon": "🤝"
            },
            {
                "name": "Small Talk",
                "description": "Improve casual conversation skills for networking events, coffee breaks, and professional socializing.",
                "category": "Social",
                "icon": "☕"
            },
            {
                "name": "Phone Calls",
                "description": "Practice clear pronunciation for telephone conversations, voicemails, and conference calls.",
                "category": "Business",
                "icon": "📞"
            },
            {
                "name": "Job Interviews",
                "description": "Prepare for interviews by practicing answers to common questions with perfect pronunciation.",
                "category": "Career",
                "icon": "👔"
            },
            {
                "name": "Customer Service",
                "description": "Learn professional phrases for customer interactions, handling complaints, and providing assistance.",
                "category": "Business",
                "icon": "🛎️"
            }
        ]

        # Create topic objects
        for topic_data in topics:
            topic = Topic(**topic_data)
            db.add(topic)

        # Commit to database
        db.commit()
        print(f"✓ Successfully seeded {len(topics)} topics!")

        # Display created topics
        print("\nCreated topics:")
        for topic in topics:
            print(f"  - {topic['icon']} {topic['name']} ({topic['category']})")

    except Exception as e:
        print(f"Error seeding topics: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_topics()
