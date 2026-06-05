# Mutual Fund FAQ Assistant: Detailed Architecture & Design Specification

This document provides a comprehensive specification of the architecture, design choices, data flow, compliance boundaries, and components of the **Facts-Only Mutual Fund FAQ Assistant**. It integrates the product goals, target audience, ingestion requirements, RAG implementation, and regulatory boundaries to guide development.

---

## 1. Project Background & Objectives

The goal of this project is to design and implement a lightweight **Retrieval-Augmented Generation (RAG)-based FAQ Assistant** for mutual fund schemes. 

* **Product Context Reference:** Groww (premium, clean, visual-first interface).
* **Core Philosophy:** **Facts-only**. The assistant must answer objective, verifiable queries by retrieving information *exclusively* from official, public, and regulatory sources.
* **Compliance & Advisory Limits:** The assistant must **strictly avoid** providing investment advice, opinions, recommendations, performance comparisons, or return calculations.

### Target Users
1. **Retail Investors:** Users comparing mutual fund schemes or looking for specific, factual details (fees, loads, minimums, etc.).
2. **Support & Content Teams:** Internal teams addressing high volumes of repetitive, factual mutual fund queries.

---

## 2. Scope & Corpus Definition

### 2.1 Asset Management Company & Schemes
We select **HDFC Mutual Fund** as the target AMC, indexing the Groww direct growth pages for **5 distinct schemes** across diverse asset classes:
1. **HDFC Mid-Cap Opportunities Fund** - Mid Cap equity scheme.
   [Source URL](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
2. **HDFC Small Cap Fund** - Small Cap equity scheme.
   [Source URL](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)
3. **HDFC Gold ETF Fund of Fund** - FoF scheme tracking Gold.
   [Source URL](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth)
4. **HDFC Multi Cap Fund** - Multi Cap equity scheme.
   [Source URL](https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth)
5. **HDFC Large Cap Fund** - Large Cap equity scheme.
   [Source URL](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)

### 2.2 Document Collection (19 Source URLs)
The ingestion corpus comprises official AMC details, factsheets, SIDs, and educational links for these schemes, specifically targeting the direct data sources for the 5 selected funds.
* **Factsheets:** Monthly factsheet PDFs/links for each of the 5 schemes.
* **SIDs & KIMs:** Scheme Information Documents (SIDs) and Key Information Memorandums (KIMs) containing legal definitions.
* **Instructional Pages:**
  * How to download account statement from HDFC Mutual Fund.
  * How to download capital gains statement / consolidated account statement (CAS).
  * HDFC Mutual Fund Help/FAQ section.
* **Regulatory/Educational Links:**
  * AMFI Investor Education guide.
  * SEBI Investor Protection FAQs.

### 2.3 Query Requirements
The assistant is designed to resolve factual queries including:
* Expense ratios of selected schemes.
* Exit load structures.
* Minimum SIP/lump sum amounts.
* Lock-in periods (especially for the ELSS Tax Saver).
* Riskometer classifications.
* Benchmark indexes.
* How-to steps for downloading statements or capital gains reports.

---

## 3. Key Constraints & Guiding Rules

To ensure strict compliance with financial regulations and user safety, the system adheres to the following rules:

> [!IMPORTANT]
> **Advisory Restrictions**
> No investment advice, recommendations, performance comparisons, or return calculations are allowed. Performance-related queries must bypass calculations and redirect the user directly to the official factsheet URL.

> [!CAUTION]
> **Privacy & Security (PII Protection)**
> The system is **strictly prohibited** from collecting, storing, or processing Personally Identifiable Information (PII) or credentials, including:
> * PAN (Permanent Account Number)
> * Aadhaar numbers
> * Bank account numbers / Portfolio folios
> * OTPs (One-Time Passwords)
> * User email addresses or phone numbers

> [!NOTE]
> **Output Grounding**
> * **Length Limit:** Maximum of **3 sentences** per response.
> * **Citations:** Exactly **one** clear source citation link per response.
> * **Footer:** Every response must end with: `“Last updated from sources: <date>”`.

---

## 4. System Architecture Overview

The system follows a modular, three-tier architecture:
1. **Frontend (User Interface):** A premium, lightweight React/Vite application styled with Groww-inspired Vanilla CSS (dark-mode aesthetic, custom glassmorphism, responsive layout).
2. **Backend (API Service):** A Python FastAPI service that manages the RAG execution pipeline, query filtering, and retrieval orchestration.
3. **Data & Storage Layer:** A local Vector Database (Chroma/FAISS) coupled with a metadata store for managing chunks, URLs, and scheme properties.

![System Architecture Flowchart](https://mermaid.ink/img/Z3JhcGggVEQKICAgICUlIEZyb250ZW5kIFRpZXIKICAgIHN1YmdyYXBoIFVJIFsiRnJvbnRlbmQgKFJlYWN0L1ZpdGUpIl0KICAgICAgICBBW1VzZXIgSW5wdXRdIC0tPnwxLiBQT1NUIC9xdWVyeXwgQihDaGF0IEludGVyZmFjZSkKICAgICAgICBCIC0tPnxEaXNwbGF5IFJlc3BvbnNlfCBDW0Fuc3dlciAvIFJlamVjdGlvbiArIENpdGF0aW9uICsgRm9vdGVyXQogICAgZW5kCgogICAgJSUgQmFja2VuZCBUaWVyCiAgICBzdWJncmFwaCBBUEkgWyJCYWNrZW5kIChGYXN0QVBJKSJdCiAgICAgICAgQiAtLT58UXVlcnkgQVBJfCBEe0Fkdmlzb3J5IEd1YXJkcmFpbH0KICAgICAgICBEIC0tPnxJcyBBZHZpc29yeT98IEVbUmVmdXNhbCBFbmdpbmVdCiAgICAgICAgRCAtLT58SXMgRmFjdHVhbD98IEZbUmV0cmlldmFsIEVuZ2luZV0KICAgICAgICAKICAgICAgICBFIC0tPnxSZXR1cm4gUmVqZWN0aW9uIHdpdGggQU1GSSBMaW5rfCBCCiAgICAgICAgCiAgICAgICAgJSUgUmV0cmlldmFsICYgR2VuZXJhdGlvbgogICAgICAgIEYgLS0+fDIuIFNlYXJjaCBWZWN0b3IgU3RvcmV8IEdbKFZlY3RvciBEQiAtIENocm9tYSldCiAgICAgICAgRyAtLT58My4gUmV0dXJuIFRvcCBLIENodW5rc3wgSFtDb250ZXh0IEFnZ3JlZ2F0b3IgYW5kIFJlcmFua2VyXQogICAgICAgIEggLS0+fDQuIFN0cnVjdHVyZWQgQ29udGV4dHwgSVtMTE0gR2VuZXJhdGlvbiBFbmdpbmVdCiAgICAgICAgSSAtLT58NS4gUmF3IFJlc3BvbnNlfCBKW1Bvc3QtR2VuZXJhdGlvbiBWYWxpZGF0b3JdCiAgICAgICAgSiAtLT58Ni4gVmVyaWZpZWQgQW5zd2VyfCBCCiAgICBlbmQKCiAgICAlJSBJbmdlc3Rpb24gUGlwZWxpbmUKICAgIHN1YmdyYXBoIEluZ2VzdGlvbiBbIk9mZmxpbmUgSW5nZXN0aW9uIFBpcGVsaW5lIl0KICAgICAgICBLW1NvdXJjZXM6IFBERiBGYWN0c2hlZXRzL1NJRHMvRkFRc10gLS0+fERvd25sb2FkICYgUGFyc2V8IExbRG9jdW1lbnQgUGFyc2VyXQogICAgICAgIEwgLS0+fENodW5rICYgQW5ub3RhdGUgTWV0YWRhdGF8IE1bVGV4dCBFbWJlZGRpbmdzIEdlbmVyYXRvcl0KICAgICAgICBNIC0tPnxTYXZlIFZlY3RvcnN8IEcKICAgIGVuZA==)

---

## 5. Ingestion & Indexing Pipeline (Offline)

Since the mutual fund corpus is relatively static and updates monthly or quarterly (e.g., factsheets are published monthly), a batch/offline ingestion pipeline is optimal.

### 5.1 Ingestion Flow
1. **Document Downloader:** A script fetches the PDF files and HTML FAQs, caching them locally in a `raw_data/` directory.
2. **Document Parser:**
   - **HTML Parser:** Extracts clean text from FAQ pages using BeautifulSoup, removing scripts, footers, and headers.
   - **PDF Parser:** Uses `pdfplumber` or `pypdf` to extract text. Special attention is paid to tables (which contain key data like exit loads, expense ratios, and minimum investment amounts). Tabular data is parsed and serialized into a clean Markdown table format to preserve structural relationships for the LLM.
3. **Semantic Chunking:**
   - Chunks are created using a recursive character text splitter with a chunk size of `512` characters and an overlap of `64` characters.
   - Each Markdown table is treated as a single, isolated chunk to prevent table rows from being separated.
4. **Metadata Annotation:** Every chunk is tagged with:
   - `source_url`: The official URL to the source document.
   - `scheme_name`: The scheme it belongs to (or `General` / `Regulatory`).
   - `document_type`: `Factsheet`, `SID`, `KIM`, `FAQ`, or `Guide`.
   - `last_updated`: The publication/fetch date (e.g., `May 31, 2026`).
5. **Vector Store Injection:** Chunks are embedded using a BGE embedding model (e.g., local `BAAI/bge-small-en-v1.5` or any BGE model suitable for mutual fund factsheet data) and stored in a local **Chroma** database.

### 5.2 Ingestion Scheduler (GitHub Actions)
To ensure that the vector database is automatically updated, we implement a **GitHub Actions Workflow** as the ingestion scheduler.
* **Frequency:** Daily execution at **3:30 PM IST** (10:00 AM UTC).
* **Trigger Event:** cron schedule `0 10 * * *`.
* **Execution Tasks:**
  1. Sets up Python and installs dependencies (`requirements.txt`).
  2. Runs `python ingestion/download.py` to fetch updated factsheets and FAQ documents.
  3. Runs `python ingestion/parser.py` and `python ingestion/index.py` to rebuild or update the vector index.
  4. Saves/commits the persistent Chroma DB state back to the repository (or remote storage if preferred).

Below is the concrete workflow configuration (`.github/workflows/ingest_scheduler.yml`):

```yaml
name: Daily Mutual Fund Data Ingestion

on:
  schedule:
    # 3:30 PM IST is 10:00 AM UTC daily
    - cron: '0 10 * * *'
  workflow_dispatch: # Allows manual triggering from the GitHub UI

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'
          cache-dependency-path: 'backend/requirements.txt'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt

      - name: Run Ingestion Pipeline
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          python ingestion/download.py
          python ingestion/parser.py
          python ingestion/index.py

      - name: Commit and Push Updated Database
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add chroma_db/ raw_data/
          git commit -m "Auto-update: Daily ingestion run $(date -u +'%Y-%m-%d %H:%M:%S UTC')" || echo "No changes to commit"
          git push
```


---

## 6. Query Processing & Retrieval Pipeline (Online)

The retrieval process enforces compliance and factual grounding before sending any prompt to the LLM.

![Query Processing and Retrieval Sequence Diagram](https://mermaid.ink/img/c2VxdWVuY2VEaWFncmFtCiAgICBhdXRvbnVtYmVyCiAgICBhY3RvciBVc2VyCiAgICBwYXJ0aWNpcGFudCBVSSBhcyAiQ2hhdCBVSSAoVml0ZSkiCiAgICBwYXJ0aWNpcGFudCBHdWFyZCBhcyAiQWR2aXNvcnkgR3VhcmRyYWlsIChMTE0vQ2xhc3NpZmllcikiCiAgICBwYXJ0aWNpcGFudCBSZXRyaWV2ZXIgYXMgIlJldHJpZXZhbCBFbmdpbmUiCiAgICBwYXJ0aWNpcGFudCBWREIgYXMgIkNocm9tYSBWZWN0b3IgU3RvcmUiCiAgICBwYXJ0aWNpcGFudCBMTE0gYXMgIkxMTSAoR3JvcSkiCiAgICBwYXJ0aWNpcGFudCBWYWxpZGF0b3IgYXMgIlJlc3BvbnNlIFZhbGlkYXRvciIKCiAgICBVc2VyLT4+VUk6ICJUeXBlcyBxdWVyeSAoZS5nLiwgJ1doYXQgaXMgdGhlIGV4aXQgbG9hZCBvZiBIREZDIEZsZXhpIENhcD8nKSIKICAgIFVJLT4+R3VhcmQ6ICJQT1NUIC9xdWVyeSB7dGV4dDogcXVlcnl9IgogICAgCiAgICByZWN0IHJnYmEoMjQwLCAyNDgsIDI1NSwgMC4xKQogICAgICAgIE5vdGUgb3ZlciBHdWFyZDogUGhhc2UgMTogQ29tcGxpYW5jZSBDaGVjawogICAgICAgIEd1YXJkLT4+R3VhcmQ6ICJFdmFsdWF0ZSBpZiBxdWVyeSByZXF1ZXN0cyBhZHZpc29yeSwgcmV0dXJucywgb3Igb3BpbmlvbnMiCiAgICAgICAgYWx0IElzIEFkdmlzb3J5L1NwZWN1bGF0aXZlPwogICAgICAgICAgICBHdWFyZC0tPj5VSTogIlJlZnVzYWwgcmVzcG9uc2UgKyBTRUJJIEVkdWNhdGlvbmFsIExpbmsiCiAgICAgICAgZW5kCiAgICBlbmQKCiAgICByZWN0IHJnYmEoMjU1LCAyNTAsIDI0MCwgMC4xKQogICAgICAgIE5vdGUgb3ZlciBSZXRyaWV2ZXIsIFZEQjogUGhhc2UgMjogUmV0cmlldmFsCiAgICAgICAgR3VhcmQtPj5SZXRyaWV2ZXI6ICJQcm9jZWVkIHdpdGggZmFjdHVhbCBxdWVyeSIKICAgICAgICBSZXRyaWV2ZXItPj5WREI6ICJRdWVyeSBlbWJlZGRpbmdzIHNlYXJjaCArIE1ldGFkYXRhIEZpbHRlciIKICAgICAgICBWREItLT4+UmV0cmlldmVyOiAiUmV0dXJuIFRvcCA0IGNvbnRleHQgY2h1bmtzIgogICAgICAgIFJldHJpZXZlci0+PlJldHJpZXZlcjogIlJlcmFuayBjaHVua3MgKFByaW9yaXRpemUgdGFibGUgbWV0cmljcykiCiAgICBlbmQKCiAgICByZWN0IHJnYmEoMjQ1LCAyNTUsIDI1MCwgMC4xKQogICAgICAgIE5vdGUgb3ZlciBMTE0sIFZhbGlkYXRvcjogUGhhc2UgMzogRmFjdHMgR2VuZXJhdGlvbiBhbmQgVmFsaWRhdGlvbgogICAgICAgIFJldHJpZXZlci0+PkxMTTogIlByb21wdCB3aXRoIHN0cmljdCBzeXN0ZW0gY29uc3RyYWludHMgKyBDb250ZXh0IENodW5rcyIKICAgICAgICBMTE0tLT4+VmFsaWRhdG9yOiAiRawgY29tcGxldGlvbiAobWF4IDMgc2VudGVuY2VzICsgY2l0YXRpb24gbGluaykiCiAgICAgICAgVmFsaWRhdG9yLT4+VmFsaWRhdG9yOiAiVmVyaWZ5IGxlbmd0aCBpcyBsZXNzIHRoYW4gb3IgZXF1YWwgdG8gMyBzZW50ZW5jZXMgYW5kIGhhcyBmb290ZXIiCiAgICAgICAgVmFsaWRhdG9yLS0+PlVJOiAiSlNPTiByZXNwb25zZSB7IGFuc3dlciwgY2l0YXRpb24sIGxhc3RfdXBkYXRlZCB9IgogICAgZW5kCiAgICAKICAgIFVJLT4+VXNlcjogIlJlbmRlcnMgZm9ybWF0dGVkLCBzdHlsZWQgY2hhdCBidWJibGUiCg==)

### 6.1 Advisory Guardrail (Classification Step)
Before retrieving, the query is analyzed by a fast classifier (either a small fine-tuned classifier or a system-prompted LLM function call).
* **Advisory Class:** Queries asking for recommendations, predicting performance, or asking "should I buy X?".
  * *Response:* Bypasses RAG. Returns: *"I cannot provide investment advice or scheme recommendations. You can learn more about objective investing on the [AMFI Investor Education Portal](https://www.amfiindia.com/investor-corner/education-series)."*
* **Factual Class:** Queries asking about fees, lock-in periods, exit loads, and administration details.
  * *Response:* Proceed to Retrieval.

### 6.2 Context Retrieval & Reranking
1. **Embedding Search:** The query is embedded and searched against the Vector DB.
2. **Metadata Filtering:** If the query names a specific scheme (e.g., "ELSS"), a metadata filter is applied to retrieve chunks tagged with `scheme_name = "HDFC ELSS Tax Saver"` or `General`.
3. **Reranking Heuristics:**
   - Retranslates typical synonyms (e.g., "expense" -> "expense ratio", "charges" -> "exit load").
   - Boosts chunks containing numeric table figures or structured lists.

---

## 7. LLM Generation & Post-Processing Guardrails

To meet the strict compliance and formatting constraints, we implement a dual-layered guardrail approach: prompt-level instructions and post-generation code validation.

### 7.1 System Prompt Design
The LLM is configured with a strict system prompt:

```text
You are the Mutual Fund FAQ Assistant, a compliant, facts-only RAG assistant.
Your goal is to answer factual queries about mutual funds using ONLY the provided context.

CONSTRAINTS:
1. Speak exclusively in facts. Do NOT offer opinions, ratings, or advice.
2. Never recommend any scheme or suggest that a user invest.
3. Keep your response short and concise. Do NOT exceed 3 sentences in total.
4. Cite exactly ONE official URL from the context as the source. Provide it as a standard Markdown link.
5. If the context does not contain the answer, politely state that you do not have that factual information, and refuse to speculate.
6. For performance/returns queries, refuse to calculate or display returns and instead redirect the user to the official factsheet citation URL.
```

### 7.2 Post-Generation Validator
A python function intercepts the LLM output and validates it:
1. **Sentence Counter:** Splitting the text by period markers and verifying it has $\le 3$ sentences. If it exceeds this, it truncates the answer cleanly or triggers a short re-prompt.
2. **Citation Verifier:** Validates that the citation URL present in the response matches one of the URLs in the retrieved context chunks (protecting against LLM hallucination).
3. **Footer Appender:** Automatically appends the required compliance footer using the `last_updated` date extracted from the retrieved chunk's metadata:
   `Last updated from sources: May 31, 2026`

---

## 8. User Interface Mockup & Styling

The frontend will be a single-page React app with a premium, responsive layout.

### 8.1 Color Palette & Typography
* **Background:** Sleek Dark Slate (`#0B0E11`) with card backgrounds in dark grey (`#15191E`).
* **Accents:** Groww-inspired Vibrant Green (`#00D09C`) and subtle borders in Cool Grey (`#2E353F`).
* **Text:** High contrast white for headers (`#FFFFFF`), muted grey for body text (`#9AA4B2`).
* **Typography:** Modern Sans-Serif font (`Outfit` or `Inter` from Google Fonts).

### 8.2 Layout Elements
1. **Header:** Features the app name, a status indicator ("Live Data Connection"), and a prominent warning badge:
   `⚠️ Facts-only. No investment advice.`
2. **Welcome Screen:** Displays:
   - A descriptive greeting explaining the assistant's scope.
   - Three clickable quick-start questions:
     1. *"What is the exit load of the HDFC Mid-Cap Opportunities Fund?"*
     2. *"How do I download my Consolidated Account Statement (CAS)?"*
     3. *"What is the minimum investment for the HDFC Small Cap Fund?"*
3. **Chat Container:** Shows the message history with smooth scrolling and animations.
4. **Input Area:** A clean text bar with a submit button. Underneath the input bar, a persistent footer reads:
   `Note: This assistant retrieves factual data directly from official HDFC AMC, SEBI, and AMFI sources. It does not provide financial planning or advisory services.`

---

## 9. Implementation Roadmap

![Implementation Roadmap Gantt Chart](https://mermaid.ink/img/Z2FudHQKICAgIHRpdGxlIEZBUSBBc3Npc3RhbnQgSW1wbGVtZW50YXRpb24gU2NoZWR1bGUKICAgIGRhdGVGb3JtYXQgIFlZWVktTU0tREQKICAgIHNlY3Rpb24gUGhhc2UgMTogRGF0YSBhbmQgUGlwZWxpbmUKICAgIERlZmluZSBDb3JwdXMgYW5kIEZldGNoIERvY3VtZW50cyAgOmFjdGl2ZSwgMjAyNi0wNi0wNSwgMWQKICAgIEltcGxlbWVudCBQYXJzZXIgYW5kIENodW5raW5nIFNjcmlwdDogMjAyNi0wNi0wNiwgMWQKICAgIFNldHVwIENocm9tYSBhbmQgVmVjdG9yaXplIERhdGEgICAgOiAyMDI2LTA2LTA3LCAxZAogICAgc2VjdGlvbiBQaGFzZSAyOiBSQUcgQmFja2VuZAogICAgQnVpbGQgQWR2aXNvcnkgR3VhcmRyYWlsIEFQSSAgICAgOiAyMDI2LTA2LTA4LCAxZAogICAgRGV2ZWxvcCBSZXRyaWV2YWwgYW5kIFJlcmFua2VyICAgICA6IDIwMjYtMDYtMDksIDFkCiAgICBJbXBsZW1lbnQgR2VuZXJhdGlvbiBhbmQgVmFsaWRhdG9yIDogMjAyNi0wNi0xMCwgMWQKICAgIHNlY3Rpb24gUGhhc2UgMzogRnJvbnRlbmQgYW5kIFVJCiAgICBDcmVhdGUgVml0ZSBBcHAgYW5kIENTUyBUaGVtZSAgICAgIDogMjAyNi0wNi0xMSwgMWQKICAgIEJ1aWxkIENoYXQgYW5kIFdlbGNvbWUgQ29tcG9uZW50cyAgIDogMjAyNi0wNi0xMiwgMWQKICAgIEludGVncmF0ZSBBUEkgYW5kIFRlc3QgVUkgRmxvd3MgICAgOiAyMDI2LTA2LTEzLCAxZA==)
