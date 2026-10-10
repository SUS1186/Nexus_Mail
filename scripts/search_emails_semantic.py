import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.email import EmailMessage
from app.services.nlp_service import NLPService

def search_inbox(query: str, top_k: int = 3):
    print(f"\nSearching for: '{query}'")
    nlp = NLPService()
    query_vector = nlp.generate_embedding(query)

    db = SessionLocal()
    try:
        # Cosine distance: 0.0 means identical, values closer to 0 mean higher similarity
        results = (
            db.query(
                EmailMessage,
                EmailMessage.embedding.cosine_distance(query_vector).label("distance")
            )
            .filter(EmailMessage.embedding.isnot(None))
            .order_by("distance")
            .limit(top_k)
            .all()
        )

        print("\n" + "=" * 85)
        print(f"{'Rank':<5} | {'Cosine Dist':<12} | {'Category':<20} | {'Subject':<40}")
        print("=" * 85)

        for rank, (email, distance) in enumerate(results, 1):
            print(f"{rank:<5} | {distance:<12.4f} | {email.category:<20} | {email.subject[:38]}")

        print("=" * 85)

        if results:
            top_email, top_dist = results[0]
            print(f"\nTop Match Snippet: \"{top_email.snippet[:160]}...\"")

    finally:
        db.close()

if __name__ == "__main__":
    # Test query 1: Finding event/application deadlines
    search_inbox("hackathon application deadline")
    
    # Test query 2: Finding account security alerts
    search_inbox("account password and authentication")