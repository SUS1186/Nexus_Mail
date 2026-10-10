# Nexus Mail 📨⚡

> **Autonomous Multi-Account AI Email Classification, Semantic Search & Dispatch Assistant**[cite: 4]  
> Built with FastAPI, SentenceTransformers (`all-MiniLM-L6-v2`), Neon PostgreSQL (`pgvector`), and Google Gemini 2.5 Flash[cite: 4].

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-Neon_pgvector-336791.svg)](https://neon.tech/)
[![Model](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-8E75C4.svg)](https://ai.google.dev/)
[![Embeddings](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

---

## 📌 Overview

Managing high-volume inboxes creates cognitive fatigue as critical competition deadlines, authentication codes, and sponsorship requests get lost under automated newsletters and spam[cite: 4].

**Nexus Mail** solves this through a local-first, privacy-focused hybrid architecture[cite: 4]:
* **Local Ingestion & NLP**: Decodes raw MIME emails over OAuth 2.0 and classifies them across 7 intent categories with a priority score (0–5) and reply necessity verdict[cite: 4].
* **Local Dense Embeddings**: Generates 384-dimensional dense vectors on the CPU in $<15\text{ ms}$ using `all-MiniLM-L6-v2` without sending private content to third-party embedding APIs[cite: 4].
* **Serverless Vector Storage**: Leverages Neon PostgreSQL with the `pgvector` extension to perform sub-millisecond cosine distance (`<=>`) queries for conceptual search[cite: 4].
* **Grounded Synthesis**: Prompts Google Gemini 2.5 Flash with the retrieved conversation context and selected tone to generate context-aware draft replies without hallucinations[cite: 4].
* **Human-in-the-Loop Safety**: Assembles RFC 2822 MIME drafts and pushes them directly to the user's live Gmail Drafts folder without ever sending messages autonomously[cite: 4].

---

## 🔄 Execution Pipeline & Flow Cards


```

[ Gmail API ] ──(OAuth 2.0)──► [ Multi-Tier NLP ] ──► [ all-MiniLM-L6-v2 ]
(7 Categories)        (384-dim Embeddings)
│
[ Gmail Drafts ] ◄──(RFC 2822)── [ Gemini 2.5 Flash ] ◄── [ Neon pgvector ]
(Human Review)                   (Context Drafting)     (Cosine Distance)

```

| Phase | Flow Card | Primary Operation | Output Artifact |
| :---: | :--- | :--- | :--- |
| **01** | 📥 **OAuth Ingestion & Preprocessing** | Connects to Gmail API v1 using OAuth 2.0 (`token.json`), fetches batches of raw MIME envelopes, parses multipart payloads, and strips HTML/CSS boilerplate[cite: 4]. | Cleaned plaintext, sender headers, and thread metadata[cite: 4]. |
| **02** | 🏷️ **Multi-Tier NLP & Reply Verdict** | Heuristically maps message content to 7 intent categories, assigns a priority score (0–5), and assesses automated patterns to determine reply necessity[cite: 4]. | Category tag, Priority Score, and Reply Verdict (`Reply Recommended` / `Optional Acknowledgment` / `No Reply Needed`)[cite: 4]. |
| **03** | 🧬 **Dense Vector Embedding** | Runs the local SentenceTransformer model `all-MiniLM-L6-v2` with mean pooling and L2 unit normalization on local CPU/GPU hardware[cite: 4]. | Normalized 384-dimensional float vector array[cite: 4]. |
| **04** | 🗄️ **pgvector Indexing & Search** | Stores relational metadata alongside dense vector embeddings inside Neon Serverless PostgreSQL using the `<=>` cosine distance operator[cite: 4]. | Sub-millisecond similarity rankings for conceptual semantic queries[cite: 4]. |
| **05** | ✍️ **Gemini 2.5 Flash Synthesis** | Injects sender identity, snippet context, and thread history into Gemini 2.5 Flash with user-steered tone settings (*Formal* vs. *Concise*)[cite: 4]. | Grounded, factual, context-aware draft reply[cite: 4]. |
| **06** | 📬 **Two-Way Gmail Draft Injection** | Formats an RFC 2822 URL-safe Base64 payload preserving `threadId` and calls `users.drafts.create` to sync the response directly into Gmail[cite: 4]. | Editable draft waiting inside the user's Gmail thread[cite: 4]. |

---

## ✨ Features

* **Widescreen Modern Dashboard**: High-density interface with live telemetry badges for synchronized messages, pending replies, and vector status[cite: 4].
* **7 Intent Categories**:
  * 🟣 **Educational & Hackathons** (Shortlists, round advancements, team submissions)[cite: 4]
  * 🟡 **Action Required** (Form submissions, direct requests, immediate tasks)[cite: 4]
  * 🔴 **Security Alerts** (2FA codes, password updates, unauthorized access alerts)[cite: 4]
  * 🔵 **Sponsorships & Collabs** (Partnerships, commercial brand inquiries)[cite: 4]
  * 🔷 **Subscriptions & Billing** (Invoices, transaction receipts, account statements)[cite: 4]
  * 🟢 **Marketing & Promotions** (Newsletters, discount campaigns)[cite: 4]
  * ⛔ **Spam** (Phishing indicators, unsolicited broadcasts)[cite: 4]
* **Reply Necessity Indicators**: Tags emails as `💬 Reply Recommended`, `✨ Optional Acknowledgment`, or `🔕 No Reply Needed` to minimize decision fatigue[cite: 4].
* **Dense Semantic Search**: Natural language query engine using vector similarity rather than exact keyword matches[cite: 4].
* **Account Switcher**: Dedicated modal allowing users to disconnect active sessions and link different Google accounts.
* **Human-in-the-Loop Protocol**: Zero automated sending; the user retains full editorial control before dispatching any communication[cite: 4].
* **Diagnostic Boot Splash**: Boot-up screen that verifies local embedding weights, Gemini API status, and Neon database connectivity.

---

## 🛠️ Tech Stack

* **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (ASGI) with [Uvicorn](https://www.uvicorn.org/)[cite: 4]
* **Database & Vector Store**: [Neon PostgreSQL](https://neon.tech/) with [`pgvector`](https://github.com/pgvector/pgvector)[cite: 4]
* **Local Embedding Engine**: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)[cite: 4]
* **Large Language Model**: [Google Gemini 2.5 Flash](https://ai.google.dev/)[cite: 4]
* **Mail API & Standards**: Google Gmail API v1, OAuth 2.0, RFC 2822 MIME[cite: 4]
* **Frontend UI**: Single Page Application (SPA) using HTML5, Tailwind CSS, and Heroicons

---

## 📋 Prerequisites

Before setting up the project, make sure you have:
* **Python 3.10+** installed on your system.
* **Git** installed.
* A **Neon Database** account with a PostgreSQL instance (with `pgvector` enabled).
* A **Google Cloud Console** project with the **Gmail API** enabled and OAuth 2.0 Desktop credentials.
* A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

---

## ⚡ Quickstart & Installation

Follow these steps to clone, configure, and run the project locally on your machine.

### Step 1: Clone the Repository[cite: 5]
```bash
git clone [https://github.com/SUS1186/Nexus_Mail.git](https://github.com/SUS1186/Nexus_Mail.git)
cd Nexus_Mail

```

### Step 2: Set Up Virtual Environment

**On Windows (PowerShell):**

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

```

**On Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory:

```ini
DATABASE_URL=postgresql://<username>:<password>@<neon_host>.neon.tech/<dbname>?sslmode=require
GEMINI_API_KEY=your_gemini_api_key_here

```

### Step 5: Add Google OAuth Credentials

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API** under **APIs & Services**.
3. Configure the **OAuth Consent Screen** (User Type: External, add your email under Test Users).
4. Go to **Credentials** $\rightarrow$ **Create Credentials** $\rightarrow$ **OAuth Client ID**.
5. Select **Desktop Application** as the application type.
6. Download the generated client secret JSON file, rename it to `credentials.json`, and place it in the root folder of the project:
```text
Nexus_Mail/
├── credentials.json   <-- Place file here
├── .env
└── ...

```



### Step 6: Initialize Database Schema

Run the migration script to verify your database connection and create the `reply_verdict` column:

```powershell
python scripts/add_column.py

```

### Step 7: Launch the Server

```bash
uvicorn app.main:app --reload

```

Once running, navigate to **`http://127.0.0.1:8000`** in your browser.

---

## 🖥️ Usage Guide

1. **Initial Boot**: The system diagnostics screen checks the embedding model, Gemini API, and Neon database connection.
2. **Account Connection**: Click **Sign in with Google** to complete the OAuth 2.0 handshake and generate `token.json`.
3. **Inbox Synchronization**: Click **Sync Inbox** to ingest the latest 50 emails and run the NLP classification and vector embedding pipeline.
4. **Semantic Search**: Use the search input or press `/` to search your emails conceptually (e.g., *"shortlist round results"*).
5. **AI Draft Generation**: Select any email to review context and reply recommendations. Select a tone (*Formal & Professional* or *Concise & Direct*) and click **Generate Contextual Draft**.
6. **Push to Gmail**: Click **Push to Gmail Drafts** to write the response into your actual Gmail thread. Review and dispatch the email directly in Gmail.

---

## 📁 Repository Structure

```text
Nexus_Mail/
├── app/
│   ├── db/
│   │   └── session.py            # SQLAlchemy database engine & pool configuration
│   ├── models/
│   │   └── email.py              # PostgreSQL schema with Vector(384) column
│   ├── services/
│   │   ├── gmail_service.py      # OAuth2 flow & RFC 2822 draft injection
│   │   ├── llm_service.py        # Google Gemini 2.5 Flash prompting & synthesis
│   │   └── nlp_service.py        # SentenceTransformers & reply heuristics
│   ├── static/
│   │   └── index.html            # Dashboard SPA with dark/light theme
│   └── main.py                   # FastAPI application routes & lifecycle hooks
├── scripts/
│   ├── add_column.py             # Schema migration utility
│   └── export_diagrams_png.py    # Headless diagram export utility
├── .env                          # Local credentials (gitignored)
├── credentials.json              # Google OAuth Client Secrets (gitignored)
├── token.json                    # User session token cache (gitignored)
├── requirements.txt              # Python package dependencies
└── README.md                     # Project documentation

```

---

## 🔒 Security & Privacy

* **Zero Plaintext Credential Exposure**: Passwords are never collected or stored. Authentication relies strictly on scoped OAuth 2.0 tokens.


* **Local Feature Vectorization**: Sentence embeddings run locally on CPU, keeping raw email bodies off third-party vector clouds.


* **Human-in-the-Loop Principle**: The application uses `users.drafts.create` exclusively; `users.messages.send` is never called, eliminating the risk of accidental or hallucinated autonomous dispatches.



---

## 👥 Contributors

* **Suhassi Zalavadia**

* **Vidhi Shah**

* **Sushil Pawar**


*Department of Computer Engineering, Mukesh Patel School of Technology Management and Engineering (MPSTME)*

```
