# Mutual Fund FAQ Assistant: Phase-wise Implementation Plan

This document outlines the detailed step-by-step implementation plan to build the **Facts-Only Mutual Fund FAQ Assistant** based on [detailed_architecture.md](file:///d:/Learning/Assignment%20Projects/Mutual%20Fund%20Assistant%28RAG%20Chat%20Bot%29/docs/detailed_architecture.md).

---

## 1. Project Directory Structure

We will implement the project with the following structure:
```
├── .github/
│   └── workflows/
│       └── ingest_scheduler.yml  # GitHub Actions Daily Ingestion Workflow
├── raw_data/                 # Local directory for cached PDFs & HTMLs
├── ingestion/                # Offline pipeline scripts
│   ├── download.py
│   ├── parser.py
│   └── index.py
├── backend/                  # FastAPI Backend API
│   ├── main.py
│   ├── config.py
│   ├── guardrails.py
│   ├── retrieval.py
│   ├── generation.py
│   ├── validator.py
│   └── requirements.txt
├── frontend/                 # React/Vite Frontend UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   └── WelcomeScreen.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
└── docs/                     # Architecture & context specifications
```

---

## 2. Phase-wise Roadmap

### Phase 1: Data Ingestion & Offline Indexing Pipeline
The goal of this phase is to fetch official documents, parse them (especially handling tabular data like expense ratios and loads), chunk them semantically, and index them into a local vector database.

* **Task 1.1: Document Downloader (`ingestion/download.py`)**
  * Fetch data, factsheets, SIDs, and KIMs for the 5 selected HDFC Mutual Fund schemes (Mid-Cap Opportunities, Small Cap, Gold ETF FoF, Multi Cap, and Large Cap).
  * Fetch HTML FAQ/help guides from HDFC AMC, SEBI, and AMFI.
  * Cache them locally in `raw_data/`.
* **Task 1.2: Document Parser (`ingestion/parser.py`)**
  * Use `BeautifulSoup` to parse HTML.
  * Use `pdfplumber` to extract text from PDFs.
  * Convert PDF tables (exit load grids, expense ratios) into clean Markdown tables so formatting is preserved for the LLM.
* **Task 1.3: Semantical Chunking & Annotation (`ingestion/index.py`)**
  * Split text into semantic chunks (~512 characters with 64-character overlap).
  * Ensure table chunks are kept whole and not split in middle.
  * Annotate every chunk with metadata: `source_url`, `scheme_name`, `document_type`, and `last_updated`.
* **Task 1.4: Vector Store Ingestion**
  * Initialize a local Chroma database.
  * Embed chunks using a BGE embedding model (e.g., local `BAAI/bge-small-en-v1.5` or any suitable BGE model) that works well for this mutual fund factsheet data.
  * Store chunks and metadata in the database.
* **Task 1.5: Ingestion Scheduler (`.github/workflows/ingest_scheduler.yml`)**
  * Create a GitHub Actions workflow configuration triggered daily at 10:00 AM UTC (3:30 PM IST).
  * Configure execution steps: check out code, set up Python 3.10 with dependency caching, install dependencies from `backend/requirements.txt`, run download/parse/indexing commands in sequence, and push modified database files (`chroma_db/`, `raw_data/`) back to the git repository.
  * Refer to section 5.2 of [detailed_architecture.md](file:///d:/Learning/Assignment%20Projects/Mutual%20Fund%20Assistant%28RAG%20Chat%20Bot%29/docs/detailed_architecture.md) for the exact YAML structure.

---

### Phase 2: RAG Backend (FastAPI API Service)
Develop the core server API to process incoming user queries, filter out PII, classify advisory intent, retrieve context, call the LLM, and validate the response format.

* **Task 2.1: Pre-Filter & Advisory Guardrail (`backend/guardrails.py`)**
  * Implement regular expressions to detect and reject queries containing PII (PAN, Aadhaar, folio numbers, emails, phone numbers).
  * Build a prompt-based classifier to check if the query requests investment advice, performance calculations, or predictions. Bypasses RAG and rejects if true.
* **Task 2.2: Context Retrieval & Filtering (`backend/retrieval.py`)**
  * **Scheme Detection:** Map query keywords (`mid-cap`, `small-cap`, `gold`, `multi-cap`, `large-cap`/`top 100`) to the 5 target schemes.
  * **Strict Metadata Filtering:** If a scheme is detected, query Chroma DB using an `$or` filter: search chunks belonging to the detected scheme OR general guides (`General HDFC MF`) OR regulatory guidelines (`Regulatory AMFI`, `Regulatory SEBI`). If no scheme is detected, query the entire index. This prevents cross-fund context contamination.
  * **Tabular Reranking/Boosting:** Prioritize chunks containing Markdown tables (strings starting/ending with `|`) if the user query contains words like `load`, `ratio`, `fee`, `AUM`, or `minimum`.
  * **Ambiguity & Out-of-Scope Guardrail:** If the query contains scheme-specific terms (e.g. `exit load`, `NAV`, `expense ratio`, `minimum SIP`, `AUM`) but no target scheme is detected, the engine must return a clarifying prompt listing the 5 supported schemes. This prevents the model from returning data from random funds.
* **Task 2.3: Generation Prompt Assembly (`backend/generation.py`)**
  * Create a system prompt enforcing the compliance guidelines (facts-only, maximum 3 sentences, exactly 1 citation URL, no speculative answers) and execute calls to the Groq LLM API.
* **Task 2.4: Post-Generation Validation (`backend/validator.py`)**
  * Verify sentence count is $\le 3$.
  * Verify citation URL is valid and matches the source chunks.
  * Automatically append `Last updated from sources: <date>` footer using chunk metadata.

---

### Phase 3: Premium Frontend UI (React & Vite)
Develop a visual interface styled after Groww's visual-first design guidelines using custom dark slate Vanilla CSS.

* **Task 3.1: CSS Theme & Layout Setup (`frontend/src/index.css`)**
  * Implement the HSL design tokens: background slate (`#0B0E11`), cards slate (`#15191E`), Groww Green (`#00D09C`), and high-contrast typography (`Outfit`/`Inter`).
  * Set up a responsive layout with a header, live-connection status indicator, scroll container, and persistent disclaimer footer.
* **Task 3.2: Welcome Screen (`frontend/src/components/WelcomeScreen.jsx`)**
  * Design a greeting interface explaining the assistant's boundaries.
  * Create 3 interactive quick-start buttons that auto-fill the chat input.
* **Task 3.3: Chat Window (`frontend/src/components/ChatWindow.jsx`)**
  * Build the scrollable dialogue log with message bubbles.
  * Style user inputs in light slate bubbles and bot answers in custom glassmorphic panels.
  * Format citation links as distinct green action badges.

---

### Phase 4: Integration & Verification
Connect frontend and backend, test RAG logic, and run compliance audits.

* **Task 4.1: API Integration**
  * Configure Axios/Fetch inside React to call `POST /query`.
  * Manage loading indicators and stream response validation errors.
* **Task 4.2: Compliance Verification & Auditing**
  * Run queries requesting recommendations (e.g., "Should I buy HDFC Small Cap Fund?") and ensure they are blocked by the guardrail.
  * Run queries containing mockup PAN/Aadhaar details and verify they trigger PII rejections immediately.
  * Verify response length constraints (≤ 3 sentences) across 50 test factual queries.

---

## 3. Verification Plan

### Automated Verification
* Run unit tests on `guardrails.py` to ensure high recall on PII patterns.
* Run mock queries against the FastAPI end-point to check JSON payloads.

### Manual Verification
* Deploy backend and frontend locally, open browser, and test:
  * Exit load questions (e.g. "What is the exit load of HDFC Mid-Cap Opportunities Fund?").
  * Minimum SIP checks (e.g. "What is the minimum investment for HDFC Small Cap Fund?").
  * CAS/Statement download steps (e.g. "How to download capital gains statement?").
  * Verify layout responsiveness on mobile viewports.
