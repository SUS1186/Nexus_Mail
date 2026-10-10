# Nexus Mail 📨⚡

> **Autonomous Multi-Account AI Email Classification, Semantic Search & Dispatch Assistant**  
> Built with FastAPI, SentenceTransformers, Neon PostgreSQL (`pgvector`), and Google Gemini 2.5 Flash.

---

## 📌 Overview

Managing high-volume personal and professional inboxes leads to severe cognitive fatigue. Traditional filters only label basic spam, while modern AI extensions often upload raw, uncurated mailboxes directly to third-party APIs.

**Nexus Mail** solves this through a local-first, privacy-conscious hybrid pipeline:
1. Ingests raw emails securely through **Google OAuth 2.0**.
2. Classifies intent across 7 categories and computes a **Reply Necessity Verdict** via local NLP heuristics.
3. Embeds emails into a **384-dimensional dense vector space** locally on CPU via `all-MiniLM-L6-v2` in $<15\text{ ms}$.
4. Enables sub-millisecond semantic search inside **Neon PostgreSQL** using `pgvector`.
5. Synthesizes context-grounded, hallucination-free draft replies using **Gemini 2.5 Flash**.
6. Injects the draft directly into the native **Gmail Drafts folder** while enforcing a strict **Human-in-the-Loop (HITL)** safety boundary[cite: 4].

---

## 🚀 Execution Pipeline & Flow Cards

| Phase | Flow Card | Primary Operation | Key Output |
| :---: | :--- | :--- | :--- |
| **01** | 📥 **OAuth Ingestion & Preprocessing** | Connects to Gmail API v1 using OAuth 2.0 (`token.json`), batches up to 50 raw MIME message payloads, strips HTML/CSS boilerplate, and normalizes text[cite: 4]. | Cleaned plaintext, sender headers, and thread metadata[cite: 4]. |
| **02** | 🏷️ **Multi-Tier NLP & Reply Verdict** | Evaluates subject, snippet, and body against 7 intent categories; assigns Priority Scores (0 to 5); and evaluates sender patterns (`no-reply`, direct prompts)[cite: 4]. | Category tag, Priority Score, and `Reply Recommended` status[cite: 4]. |
| **03** | 🧬 **Dense Vector Embedding** | Runs the local transformer model `all-MiniLM-L6-v2` to mean-pool subword tokens into unit-normalized dense vectors with zero external API calls[cite: 4]. | 384-dimensional normalized float vector[cite: 4]. |
| **04** | 🗄️ **pgvector Indexing & Semantic Search** | Stores structured metadata and embeddings in Neon Serverless PostgreSQL, computing cosine distance (`<=>`) for natural language retrieval[cite: 4]. | Sub-millisecond similarity rankings for conceptual queries[cite: 4]. |
| **05** | ✍️ **Gemini 2.5 Flash Context Drafting** | Injects sender metadata, conversation snippets, and thread context into Gemini 2.5 Flash, modulated by user tone selection (*Formal* vs. *Concise*)[cite: 4]. | Grounded, hallucination-free reply draft[cite: 4]. |
| **06** | 📬 **Two-Way Gmail Draft Injection** | Assembles an RFC 2822 URL-safe Base64 payload preserving `threadId` and invokes `users.drafts.create` to sync the reply to Gmail[cite: 4]. | Draft staged in Gmail Drafts awaiting manual review[cite: 4]. |

---

## 📸 Key Features

* **Real-Time Executive Dashboard**: High-density workspace showing synchronized counts, pending reply recommendations, high-priority milestones, and vector engine status[cite: 4].
* **Intent-Based Categorization**:
  * 🟣 **Educational & Hackathons** (Shortlists, round advancements, team submissions)[cite: 4]
  * 🟡 **Action Required** (Deadlines, RSVPs, form requests)[cite: 4]
  * 🔴 **Security Alerts** (2FA notices, password modifications, authentication alerts)[cite: 4]
  * 🔵 **Sponsorships & Collabs** (Brand deals, commercial inquiries)[cite: 4]
  * 🔷 **Subscriptions & Billing** (Invoices, receipts, subscription confirmations)[cite: 4]
  * 🟢 **Marketing & Promotions** (Newsletters, discount broadcasts)[cite: 4]
  * ⛔ **Spam** (Phishing flags, unsolicited blasts)[cite: 4]
* **Reply Necessity Intelligence**: Distinguishes between emails requiring an urgent answer (`Reply Recommended`), polite acknowledgments (`Optional Acknowledgment`), and automated broadcasts (`No Reply Needed`)[cite: 4].
* **Semantic Search Engine**: Queries your inbox conceptually (e.g., *"competition shortlists"* returns hackathon updates even without keyword overlap)[cite: 4].
* **Account Switcher**: Disconnect and swap Google accounts on the fly without restarting the application.
* **Human-in-the-Loop Protocol**: The system never sends emails autonomously; it only stages drafts for user review and approval[cite: 4].
* **System Boot Diagnostics**: Interactive boot screen inspecting local embedding model weights, Neon database availability, and Gemini API readiness.

---

## 🛠️ Tech Stack

* **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (ASGI) & Uvicorn[cite: 4]
* **Database & Vector Store**: [Neon PostgreSQL](https://neon.tech/) with [`pgvector`](https://github.com/pgvector/pgvector)[cite: 4]
* **Local Embedding Engine**: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (384 Dimensions)[cite: 4]
* **Large Language Model**: [Google Gemini 2.5 Flash](https://ai.google.dev/)[cite: 4]
* **Email Protocols**: Google Gmail API v1 (OAuth 2.0, RFC 2822 MIME)[cite: 4]
* **Frontend**: Vanilla HTML5, Tailwind CSS, Heroicons

---

## 📂 Repository Structure

```text
Nexus_Mail/
├── app/
│   ├── db/
│   │   └── session.py            # SQLAlchemy session & Neon engine setup
│   ├── models/
│   │   └── email.py              # PostgreSQL schema with pgvector Column(Vector(384))
│   ├── services/
│   │   ├── gmail_service.py      # OAuth2 flow & Gmail API draft injection
│   │   ├── llm_service.py        # Google Gemini 2.5 Flash prompt synthesis
│   │   └── nlp_service.py        # SentenceTransformers & reply heuristics
│   ├── static/
│   │   └── index.html            # Single-page dashboard interface
│   └── main.py                   # FastAPI REST API endpoints
├── scripts/
│   └── add_column.py             # Schema migration utility
├── .env.example                  # Environment configuration template
├── credentials.json              # Google Cloud OAuth 2.0 Client credentials (gitignored)
├── token.json                    # Cached user OAuth tokens (gitignored)
├── requirements.txt              # Project dependencies
└── README.md
