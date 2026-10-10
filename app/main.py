import os
import threading
import time
from app.services.llm_service import LLMService
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.email import EmailMessage
from app.services.nlp_service import NLPService
from app.services.gmail_service import GmailService

app = FastAPI(
    title="AI-Powered Smart Email Assistant API",
    version="1.0.0",
    description="Backend API for email synchronization, NLP priority scoring, semantic search, and contextual draft generation."
)

# Initialize NLP service
nlp_service = NLPService()
llm_service = LLMService()

from pydantic import BaseModel

class DraftSaveRequest(BaseModel):
    draft_text: str

@app.post("/emails/{email_id}/save-draft", tags=["Smart Drafting"])
def save_gmail_draft(email_id: int, payload: DraftSaveRequest, db: Session = Depends(get_db)):
    """Pushes an edited or generated draft directly to Gmail Drafts."""
    email = db.query(EmailMessage).filter(EmailMessage.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    gmail = GmailService()
    created = gmail.create_draft(
        to=email.sender,
        subject=f"Re: {email.subject}",
        body=payload.draft_text,
        thread_id=email.thread_id
    )

    return {
        "status": "success",
        "gmail_draft_id": created.get("id"),
        "message": "Draft created in your Gmail inbox"
    }

# Serve index.html on root
@app.get("/", include_in_schema=False)
def serve_dashboard():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_file)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "email-assistant-api"}

@app.get("/emails", tags=["Emails"])
def list_emails(
    category: str = None, 
    min_priority: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    query = db.query(EmailMessage).filter(EmailMessage.priority_score >= min_priority)
    if category:
        query = query.filter(EmailMessage.category == category)
    
    records = query.order_by(EmailMessage.id.desc()).limit(limit).all()
    return [
        {
            "id": mail.id,
            "message_id": mail.message_id,
            "sender": mail.sender,
            "subject": mail.subject,
            "category": mail.category,
            "priority_score": mail.priority_score,
            "is_action_required": mail.is_action_required,
            "reply_verdict": mail.reply_verdict or "No Reply Needed",
            "snippet": mail.snippet,
            "received_at": mail.received_at
        }
        for mail in records
    ]

@app.get("/emails/search", tags=["Semantic Search"])
def semantic_search(
    q: str = Query(..., description="Natural language search query"),
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Semantic vector search using pgvector cosine distance."""
    query_vector = nlp_service.generate_embedding(q)
    results = (
        db.query(
            EmailMessage,
            EmailMessage.embedding.cosine_distance(query_vector).label("distance")
        )
        .filter(EmailMessage.embedding.isnot(None))
        .order_by("distance")
        .limit(limit)
        .all()
    )
    return [
        {
            "id": mail.id,
            "subject": mail.subject,
            "sender": mail.sender,
            "category": mail.category,
            "priority_score": mail.priority_score,
            "cosine_distance": round(distance, 4),
            "snippet": mail.snippet
        }
        for mail, distance in results
    ]

@app.post("/emails/sync", tags=["Ingestion"])
def sync_emails(max_results: int = 50, db: Session = Depends(get_db)):
    """Fetch recent emails from Gmail, run NLP classification, and store vectors."""
    gmail = GmailService()
    fetched = gmail.fetch_emails(max_results=max_results)
    new_records = 0

    for mail in fetched:
        if db.query(EmailMessage).filter(EmailMessage.message_id == mail["message_id"]).first():
            continue

        analysis = nlp_service.classify_and_score(
            subject=mail["subject"],
            sender=mail["sender"],
            snippet=mail["snippet"],
            body=mail["body"]
        )
        vector = nlp_service.generate_embedding(f"{mail['subject']}\n{mail['body']}")

        email_row = EmailMessage(
            message_id=mail["message_id"],
            thread_id=mail["thread_id"],
            sender=mail["sender"],
            subject=mail["subject"],
            body=mail["body"],
            snippet=mail["snippet"],
            received_at=mail["date"],
            category=analysis["category"],
            priority_score=analysis["priority_score"],
            is_action_required=analysis["is_action_required"],
            summary=analysis["summary"],
            embedding=vector
        )
        db.add(email_row)
        new_records += 1

    db.commit()
    return {"message": "Sync complete", "new_emails_synced": new_records}

@app.post("/emails/{email_id}/draft-reply", tags=["Smart Drafting"])
def draft_smart_reply(email_id: int, tone: str = "formal", db: Session = Depends(get_db)):
    """Context-aware auto-reply generator powered by Gemini LLM."""
    email = db.query(EmailMessage).filter(EmailMessage.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate dynamic reply via Gemini LLM based on body context and tone
    draft = llm_service.generate_reply(
        sender=email.sender,
        subject=email.subject or "",
        body=email.body or email.snippet or "",
        tone=tone
    )

    return {
        "email_id": email.id,
        "reply_to": email.sender,
        "subject": f"Re: {email.subject}",
        "suggested_draft": draft
    }
@app.post("/emails/reclassify", tags=["Ingestion"])
def reclassify_all_emails(db: Session = Depends(get_db)):
    """Re-evaluates every stored email with the latest multi-tier NLP rules."""
    emails = db.query(EmailMessage).all()
    updated = 0

    for mail in emails:
        analysis = nlp_service.classify_and_score(
            subject=mail.subject or "",
            sender=mail.sender or "",
            snippet=mail.snippet or "",
            body=mail.body or ""
        )
        mail.category = analysis["category"]
        mail.priority_score = analysis["priority_score"]
        mail.is_action_required = analysis["is_action_required"]
        mail.reply_verdict = analysis.get("reply_verdict", "No Reply Needed")
        mail.summary = analysis["summary"]
        updated += 1

    db.commit()
    return {"message": f"Successfully re-classified {updated} emails with updated NLP categories & reply verdicts."}

@app.get("/user/profile", tags=["User Profile"])
def get_user_profile():
    """Returns the profile info for the currently authenticated Google account."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return {"authenticated": False, "email": "Not Connected"}

    try:
        gmail = GmailService()
        profile = gmail.service.users().getProfile(userId='me').execute()
        return {
            "authenticated": True,
            "email": profile.get("emailAddress", "Unknown"),
            "messages_total": profile.get("messagesTotal", 0)
        }
    except Exception as e:
        return {"authenticated": False, "email": "Token Expired", "error": str(e)}

@app.post("/user/switch-account", tags=["User Profile"])
def switch_google_account():
    """Deletes token.json to trigger a fresh OAuth login on the next action."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if os.path.exists(token_path):
        os.remove(token_path)
        return {"status": "success", "message": "Account disconnected. Log in with your new email on next sync."}
    return {"status": "success", "message": "No active session found."}

@app.post("/user/clear-emails", tags=["User Profile"])
def clear_all_emails(db: Session = Depends(get_db)):
    """Wipes all emails from the database for a clean switch to another account."""
    count = db.query(EmailMessage).delete()
    db.commit()
    return {"status": "success", "message": f"Wiped {count} messages from local database."}

@app.post("/user/connect", tags=["User Profile"])
def connect_google_account():
    """Explicitly launches the Google OAuth login window and returns profile info."""
    try:
        gmail = GmailService()
        profile = gmail.service.users().getProfile(userId='me').execute()
        return {
            "status": "success",
            "authenticated": True,
            "email": profile.get("emailAddress")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google authentication failed: {str(e)}")

@app.get("/system/status", tags=["System"])
def system_startup_status(db: Session = Depends(get_db)):
    """Telemetry route reporting subsystem readiness on application boot."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    
    # 1. Check Vector Embedding Model
    nlp_ready = nlp_service.model is not None
    
    # 2. Check Gemini LLM
    llm_ready = llm_service.model is not None
    
    # 3. Check Neon PostgreSQL connection
    db_ready = False
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False
        
    # 4. Check OAuth Session
    auth_ready = os.path.exists(token_path)

    return {
        "status": "ready" if (nlp_ready and db_ready) else "initializing",
        "subsystems": {
            "embeddings": {
                "name": "SentenceTransformer (all-MiniLM-L6-v2)",
                "ready": nlp_ready
            },
            "llm": {
                "name": "Gemini 2.5 Flash",
                "ready": llm_ready
            },
            "database": {
                "name": "Neon PostgreSQL (pgvector 384-dim)",
                "ready": db_ready
            },
            "oauth": {
                "name": "Gmail OAuth2 Session",
                "ready": auth_ready
            }
        }
    }

@app.post("/system/shutdown", tags=["System"])
def shutdown_backend():
    """Gracefully terminates the FastAPI/Uvicorn backend process."""
    def kill_process():
        time.sleep(0.8)  # Brief pause to ensure the HTTP 200 response reaches the browser
        os._exit(0)      # Terminates the Uvicorn server process in PowerShell

    threading.Thread(target=kill_process, daemon=True).start()
    return {"status": "success", "message": "Nexus Mail backend engine terminated."}