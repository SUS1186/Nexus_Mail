import re
from sentence_transformers import SentenceTransformer

class NLPService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading local embedding model ({model_name})...")
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> list[float]:
        if not text.strip():
            return [0.0] * 384
        cleaned_text = re.sub(r"\s+", " ", text).strip()[:1000]
        embedding = self.model.encode(cleaned_text, normalize_embeddings=True)
        return embedding.tolist()

    def evaluate_reply_necessity(self, full_text: str, sender_lower: str) -> tuple[str, str]:
        """
        Determines whether an email necessitates an actual reply, is automated/FYI,
        or is an optional polite acknowledgment.
        """
        # 1. Obvious Automated / System notifications (No Reply Needed)
        no_reply_senders = ["no-reply", "noreply", "donotreply", "notifications@", "support@accounts.google.com"]
        if any(ns in sender_lower for ns in no_reply_senders):
            return "No Reply Needed", "Automated system dispatch — no mailbox monitor."

        no_reply_phrases = [
            "no action is needed", "do not reply to this email", "this is an automated message",
            "password was changed", "2-step verification turned on", "security alert",
            "your order has shipped", "payment receipt", "subscription renewed"
        ]
        if any(phrase in full_text for phrase in no_reply_phrases):
            return "No Reply Needed", "Informational notification or transaction summary."

        # 2. Direct Reply Prompts (Reply Recommended)
        reply_signals = [
            "please reply", "let me know", "please confirm", "rsvp", "are you available",
            "reply by", "please submit", "fill out this form", "feedback requested",
            "kindly respond", "what are your thoughts", "action required"
        ]
        if any(sig in full_text for sig in reply_signals):
            return "Reply Recommended", "Direct question or action item requiring your response."

        # 3. Congratulations / Shortlists / Advancements (Optional Acknowledgment)
        acknowledgment_signals = [
            "shortlisted", "congratulations", "selected for", "organisers will be in touch",
            "team is through to", "welcome aboard"
        ]
        if any(sig in full_text for sig in acknowledgment_signals):
            return "Optional Acknowledgment", "Status update: you can optionally acknowledge receipt."

        return "No Reply Needed", "General correspondence or broadcast update."

    def classify_and_score(self, subject: str, sender: str, snippet: str, body: str = "") -> dict:
        full_text = f"{subject} {sender} {snippet} {body}".lower()
        sender_lower = sender.lower()

        # Evaluate reply necessity
        reply_verdict, reply_reason = self.evaluate_reply_necessity(full_text, sender_lower)

        # --- 1. SPAM / PHISHING DETECTOR (Score: 0) ---
        spam_signals = [
            "claim your prize", "wire transfer", "lottery", "crypto profit", "viagra",
            "you have won", "100% free guaranteed", "urgent funds", "inheritance", "click here to claim"
        ]
        if any(sig in full_text for sig in spam_signals):
            return {
                "category": "Spam",
                "priority_score": 0,
                "is_action_required": False,
                "reply_verdict": "No Reply Needed",
                "summary": "Suspicious unsolicited broadcast."
            }

        # --- 2. HACKATHONS, SHORTLISTS & ACADEMIC ACHIEVEMENTS (Score: 5) ---
        hackathon_milestones = [
            "shortlisted", "round 1", "round 2", "finals", "selected", "swarmhack",
            "hackhost", "devfolio", "hacker house", "smart india hackathon", "sih",
            "hackathon", "devpost", "unstop", "team is through", "congratulations"
        ]
        if any(hm in full_text for hm in hackathon_milestones):
            return {
                "category": "Educational",
                "priority_score": 5,
                "is_action_required": "submit" in full_text or "rsvp" in full_text,
                "reply_verdict": reply_verdict,
                "summary": "Hackathon advancement or competition shortlist notification."
            }

        # --- 3. SECURITY & AUTH ALERTS (Score: 4) ---
        security_signals = [
            "2-step verification", "security alert", "password reset", "new sign-in",
            "unauthorized access", "verification code", "otp", "password was changed"
        ]
        if any(sig in full_text for sig in security_signals) or "no-reply@accounts.google.com" in sender_lower:
            return {
                "category": "Security Alert",
                "priority_score": 4,
                "is_action_required": "reset" in full_text or "unauthorized" in full_text,
                "reply_verdict": "No Reply Needed",
                "summary": "Account authentication or security notification."
            }

        # --- 4. SPONSORSHIPS & COLLABORATIONS (Score: 4) ---
        sponsorship_signals = [
            "sponsorship", "collab", "collaboration", "partnership proposal",
            "brand ambassador", "paid partnership", "influencer outreach"
        ]
        if any(sig in full_text for sig in sponsorship_signals):
            return {
                "category": "Sponsorships",
                "priority_score": 4,
                "is_action_required": True,
                "reply_verdict": "Reply Recommended",
                "summary": "Commercial or sponsorship proposal."
            }

        # --- 5. ACTION REQUIRED (Score: 5) ---
        action_signals = [
            "action required", "immediate attention", "deadline approaching",
            "please complete", "form submission"
        ]
        if any(sig in full_text for sig in action_signals):
            return {
                "category": "Action Required",
                "priority_score": 5,
                "is_action_required": True,
                "reply_verdict": "Reply Recommended",
                "summary": "Actionable task requiring immediate response."
            }

        # --- 6. SUBSCRIPTIONS & RECEIPTS (Score: 2) ---
        subscription_signals = [
            "receipt", "invoice", "payment received", "billing statement",
            "subscription renewed", "your order", "neon.tech", "stripe"
        ]
        if any(sig in full_text for sig in subscription_signals):
            return {
                "category": "Subscriptions",
                "priority_score": 2,
                "is_action_required": False,
                "reply_verdict": "No Reply Needed",
                "summary": "Platform subscription or transaction receipt."
            }

        # --- 7. MARKETING & PROMOTIONS (Score: 1) ---
        marketing_signals = [
            "unsubscribe", "sale", "discount", "% off", "newsletter", "shop now", "promo"
        ]
        if any(sig in full_text for sig in marketing_signals):
            return {
                "category": "Marketing",
                "priority_score": 1,
                "is_action_required": False,
                "reply_verdict": "No Reply Needed",
                "summary": "Marketing newsletter or promotional broadcast."
            }

        return {
            "category": "General",
            "priority_score": 2,
            "is_action_required": False,
            "reply_verdict": reply_verdict,
            "summary": "Standard correspondence."
        }