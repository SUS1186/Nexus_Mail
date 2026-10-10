import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None

        if not self.api_key:
            print("[LLM Warning] GEMINI_API_KEY not found in .env.")
            return

        try:
            genai.configure(api_key=self.api_key)
            
            available = [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]

            # Prioritize Flash models with active free-tier quotas
            flash_candidates = [
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-flash-lite",
                "gemini-flash-lite-latest"
            ]

            chosen_model = None
            for candidate in flash_candidates:
                for m_name in available:
                    if candidate in m_name:
                        chosen_model = m_name
                        break
                if chosen_model:
                    break

            if chosen_model:
                self.model = genai.GenerativeModel(chosen_model)
                print(f"Gemini LLM successfully initialized using: {chosen_model}!")
            else:
                print("[LLM Warning] No compatible Flash model found.")

        except Exception as e:
            print(f"[LLM Init Error] Could not connect to Gemini API: {e}")

    def generate_reply(self, sender: str, subject: str, body: str, tone: str = "formal") -> str:
        if not self.model:
            return self._fallback_reply(sender, subject, tone)

        prompt = f"""
You are an intelligent email assistant drafting a response on behalf of Suhassi.

Incoming Email Context:
- From: {sender}
- Subject: {subject}
- Content:
\"\"\"{body[:2500]}\"\"\"

Instructions:
- Tone: {tone.capitalize()} (Clear, professional, and directly addressing any questions or call-to-actions).
- Role: Suhassi.
- Draft a natural email reply addressing the specific details of the message above.
- Sign off cleanly as Suhassi.
- Output ONLY the reply email text without introductory greetings or meta labels.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[LLM Error] API generation failed: {e}")
            return self._fallback_reply(sender, subject, tone)

    def _fallback_reply(self, sender: str, subject: str, tone: str) -> str:
        sender_name = sender.split("<")[0].strip() if "<" in sender else sender
        if tone == "concise":
            return f"Hi {sender_name},\n\nReceived. I am reviewing the details regarding '{subject}' and will follow up shortly.\n\nBest,\nSuhassi"
        return (
            f"Dear {sender_name},\n\n"
            f"Thank you for your email regarding '{subject}'. "
            f"I have received the information and am reviewing the action items.\n\n"
            f"Best regards,\nSuhassi"
        )