import os
import sys

# Ensure Python discovers the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import engine

def migrate():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS reply_verdict VARCHAR DEFAULT 'No Reply Needed';"))
        conn.commit()
    print("DB column reply_verdict validated successfully!")

if __name__ == "__main__":
    migrate()