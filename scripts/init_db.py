import sys
import os

# Add parent directory to sys.path so 'app' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import engine, Base
from app.models.email import EmailMessage

def init():
    print("Connecting to Neon PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init()