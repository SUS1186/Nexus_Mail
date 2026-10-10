from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, nullable=False)
    thread_id = Column(String, index=True)
    sender = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text)
    snippet = Column(Text)
    received_at = Column(String)
    category = Column(String, default="General")
    priority_score = Column(Integer, default=0)
    is_action_required = Column(Boolean, default=False)
    reply_verdict = Column(String, default="No Reply Needed")
    summary = Column(Text)
    embedding = Column(Vector(384))