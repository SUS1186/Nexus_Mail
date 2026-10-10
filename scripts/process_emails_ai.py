import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.email import EmailMessage
from app.services.nlp_service import NLPService

def process_unclassified_emails():
    db = SessionLocal()
    nlp = NLPService()

    try:
        # Query emails that have not yet been processed
        unprocessed = db.query(EmailMessage).filter(EmailMessage.category == "Unclassified").all()

        if not unprocessed:
            print("No unclassified emails found in database.")
            return

        print(f"\nProcessing {len(unprocessed)} emails with NLP Engine...\n")

        for email in unprocessed:
            print(f"-> Analyzing: '{email.subject[:45]}'...")

            # 1. Classify intent and calculate priority
            analysis = nlp.classify_and_score(
                subject=email.subject or "",
                sender=email.sender or "",
                snippet=email.snippet or "",
                body=email.body or ""
            )

            # 2. Generate 384-dimensional vector embedding
            text_to_embed = f"Subject: {email.subject}\nFrom: {email.sender}\n{email.body or email.snippet}"
            vector = nlp.generate_embedding(text_to_embed)

            # 3. Update database record
            email.category = analysis["category"]
            email.priority_score = analysis["priority_score"]
            email.is_action_required = analysis["is_action_required"]
            email.summary = analysis["summary"]
            email.embedding = vector

        db.commit()
        print("\nAll emails successfully classified and vectorized in PostgreSQL!")

    except Exception as e:
        db.rollback()
        print(f"Error during NLP processing: {e}")
        raise
    finally:
        db.close()

def inspect_processed_results():
    db = SessionLocal()
    try:
        rows = db.query(EmailMessage).all()
        print("\n" + "=" * 80)
        print(f"{'ID':<4} | {'Priority':<8} | {'Category':<22} | {'Subject':<40}")
        print("=" * 80)
        for r in rows:
            print(f"{r.id:<4} | Score: {r.priority_score:<2} | {r.category:<22} | {r.subject[:38]}")
        print("=" * 80)
    finally:
        db.close()

if __name__ == "__main__":
    process_unclassified_emails()
    inspect_processed_results()