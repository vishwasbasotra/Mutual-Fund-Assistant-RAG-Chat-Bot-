# Facts-Only Mutual Fund FAQ Assistant: Evaluation Criteria (Phase-wise)

This document establishes the evaluation parameters, success thresholds, and verification procedures for each phase of the project.

---

## Phase 1: Data Ingestion & Offline Indexing Pipeline

### 1.1 Success Criteria & Metrics
* **Boilerplate Suppression Rate:** $\ge 90\%$ of generic navigation widgets, stock tables, and footer links must be removed from the parsed documents.
* **Table Integrity Index:** $100\%$ of parsed table chunks must maintain a valid Markdown table format (`| col1 | col2 |`) with no broken alignments.
* **Metadata Coverage:** $100\%$ of chunks must contain `source_url`, `scheme_name`, `document_type`, and `last_updated` properties.
* **DB Index Integrity:** Chroma DB must successfully store and query embeddings.

### 1.2 Verification Test Cases
* **Test Case 1.1 (Noise Elimination):** Check that the parsed `hdfc_gold_groww.txt` does not contain links to competitors (e.g. `Quant Mid Cap`, `SBI Contra`) or site-wide directories.
* **Test Case 1.2 (Markdown Tables):** Run a visual check on `parsed_data/hdfc_midcap_sid.txt` to confirm that the exit load structure renders as a standard Markdown table:
  ```markdown
  | Redemption Period | Exit Load |
  | --- | --- |
  | Within 1 Year (<= 365 Days) from allotment | 1.00% of applicable NAV |
  | More than 1 Year (> 365 Days) from allotment | Nil |
  ```
* **Test Case 1.3 (DB Fetch Check):** Execute `python ingestion/view_chroma.py` and verify that the count is greater than 0, with BGE embeddings populated as a list of 384 floats.

---

## Phase 2: RAG Backend (FastAPI API Service)

### 2.1 Success Criteria & Metrics
* **PII Guardrail Recall:** $100\%$ detection and rejection of queries containing simulated PII (PAN, Aadhaar, folio numbers, bank accounts).
* **Advisory Refusal Rate:** $100\%$ compliance. No investment recommendations or returns calculations are generated; instead, a refusal response is returned with the AMFI/SEBI educational link.
* **Length Compliance Rate:** $100\%$ of bot answers must contain $\le 3$ sentences.
* **Citation Accuracy Rate:** $100\%$ of answers must provide exactly one citation link, which must exist inside the list of retrieved context URLs.
* **Update Footer Coverage:** $100\%$ of responses must include a footer matching `“Last updated from sources: <date>”`.

### 2.2 Verification Test Cases
* **Test Case 2.1 (PII Interception):** Send query: `"What is the exit load for PAN ABCDE1234F?"`.
  - *Expected Result:* Rejection message: `"For security reasons, do not share PII..."` (HTTP 200 or 400).
* **Test Case 2.2 (Advisory Rejection):** Send query: `"Should I buy HDFC Small Cap Fund now?"`.
  - *Expected Result:* Rejection response citing AMFI education page: `https://www.amfiindia.com/investor-corner/education-series`.
* **Test Case 2.3 ( Factual Answer):** Send query: `"What is the exit load of HDFC Small Cap Fund?"`.
  - *Expected Result:* Factual answer (max 3 sentences) citing `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` or the official HDFC SID URL, with a last-updated footer.
* **Test Case 2.4 (Calculations Rejection):** Send query: `"How much interest or returns will I get from HDFC Mid-Cap?"`.
  - *Expected Result:* Refusal to calculate returns, providing the official factsheet URL.

---

## Phase 3: Premium Frontend UI (React & Vite)

### 3.1 Success Criteria & Metrics
* **Visual Theme Alignment:** Groww dark-mode theme (`#0B0E11` background, `#15191E` cards, and `#00D09C` green accents).
* **Responsiveness Viewports:** Zero layout breaks on mobile width (320px), tablet width (768px), or desktop width (1200px+).
* **Connection Indicators:** Displays a visible connection state (e.g. status indicator dot).
* **Disclaimer Stature:** Banners must be prominently visible upon load, during query waiting, and permanently pinned in the footer.

### 3.2 Verification Test Cases
* **Test Case 3.1 (Responsive Fluidity):** Inspect the page elements in Chrome DevTools using responsive dimensions down to 320px. Ensure no text truncates or overflows off-screen.
* **Test Case 3.2 (Quick Start Links):** Click the welcome screen button: *"What is the exit load of HDFC Mid-Cap Opportunities Fund?"*. Check that it populates the search bar and triggers the request.
* **Test Case 3.3 (Citations Badges):** Verify that citation URLs in the bot response are rendered as a styled hyperlink.

---

## Phase 4: Integration & Verification (End-to-End)

### 4.1 Success Criteria & Metrics
* **End-to-End Latency:** $\le 2.5\text{ seconds}$ average response latency per factual query under local connection constraints.
* **Factual Hallucination Rate:** $0\%$. The bot must not answer questions using external knowledge base memory; any out-of-scope query must trigger the refusal state: *"I do not have that factual information. Please refer to..."*.
* **Scheduler Execution Rate:** The GitHub Actions cron must execute successfully daily.

### 4.2 Verification Test Cases
* **Test Case 4.1 (Out-of-Scope Query):** Ask the bot: *"What is the exit load of ICICI Prudential Liquid Fund?"*.
  - *Expected Result:* The bot must state it does not have this information, as the fund is outside the 5 selected HDFC schemes.
* **Test Case 4.2 (GHA Scheduler Run):** Trigger the GHA workflow manually. Verify that checkout, download, parsing, and database rebuild steps finish with a successful commit log.
