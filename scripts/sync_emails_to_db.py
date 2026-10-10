import os
import sys

# Ensure Python discovers the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.email import EmailMessage
from app.services.gmail_service import GmailService

def sync_inbox(max_emails: int = 5):
    print(f"1. Fetching up to {max_emails} latest emails from Gmail...")
    gmail = GmailService()
    emails = gmail.fetch_emails(max_results=max_emails)
    
    if not emails:
        print("No emails retrieved.")
        return

    print(f"2. Connecting to database to persist records...")
    db = SessionLocal()
    new_count = 0
    skipped_count = 0

    try:
        for mail in emails:
            # Check for existing record to prevent duplicate entries
            existing = db.query(EmailMessage).filter(EmailMessage.message_id == mail["message_id"]).first()
            if existing:
                skipped_count += 1
                continue

            # Map parsed dictionary to SQLAlchemy ORM model
            email_record = EmailMessage(
                message_id=mail["message_id"],
                thread_id=mail["thread_id"],
                sender=mail["sender"],
                subject=mail["subject"],
                body=mail["body"],
                snippet=mail["snippet"],
                received_at=mail["date"],
                category="Unclassified",
                priority_score=0
            )
            db.add(email_record)
            new_count += 1

        db.commit()
        print(f"\n--- Sync Complete ---")
        print(f"New emails inserted: {new_count}")
        print(f"Duplicates skipped:  {skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"Error during synchronization: {e}")
        raise
    finally:
        db.close()

def inspect_saved_emails():
    """Query the database to verify the saved rows."""
    db = SessionLocal()
    try:
        rows = db.query(EmailMessage).order_by(EmailMessage.id.desc()).limit(5).all()
        print("\n--- Rows Currently Stored in PostgreSQL ---")
        for row in rows:
            print(f"[{row.id}] From: {row.sender[:30]} | Subject: {row.subject[:40]} | Category: {row.category}")
        print("-" * 45)
    finally:
        db.close()

if __name__ == "__main__":
    sync_inbox(max_emails=5)
    inspect_saved_emails()