# Project Context: Mutual Fund FAQ Assistant (Facts-Only Q&A)

This document provides the background, objectives, requirements, and constraints for the Mutual Fund FAQ Assistant project, based on the [problemStatement.txt](file:///d:/Learning/Assignment%20Projects/Mutual%20Fund%20Assistant%28RAG%20Chat%20Bot%29/docs/problemStatement.txt).

---

## 1. Overview & Objective

The goal of this project is to design and implement a lightweight **Retrieval-Augmented Generation (RAG)-based FAQ Assistant** for mutual fund schemes. 
* **Product Context Reference:** Groww.
* **Core Philosophy:** **Facts-only**. The assistant must answer objective, verifiable queries by retrieving information *exclusively* from official, public, and regulatory sources.
* **Compliance & Advisory Limits:** The assistant must **strictly avoid** providing investment advice, opinions, recommendations, performance comparisons, or return calculations.

---

## 2. Target Users

1. **Retail Investors:** Users comparing mutual fund schemes or looking for specific, factual details.
2. **Support & Content Teams:** Teams dealing with high volumes of repetitive, factual mutual fund queries.

---

## 3. Scope of Work

### Corpus Definition
* **AMC Selection:** Choose exactly one Asset Management Company (AMC).
* **Scheme Selection:** Choose 3–5 mutual fund schemes with diverse categories (e.g., large-cap, flexi-cap, ELSS).
* **Document Collection:** Collect 15–25 official public URLs, including:
  * Scheme factsheets
  * Key Information Memorandums (KIM)
  * Scheme Information Documents (SID)
  * AMC FAQ or help pages
  * AMFI / SEBI guidance pages
  * Guides on downloading statements and tax documents

### FAQ Assistant Requirements
The assistant must resolve factual queries like:
* Expense ratios of selected schemes
* Exit load structures
* Minimum SIP/lump sum amounts
* Lock-in periods (e.g., ELSS)
* Riskometer classifications
* Benchmark indexes
* How-to guides for downloading statements or capital gains reports

#### Response Constraints
* **Length Limit:** Maximum of **3 sentences** per response.
* **Citations:** Exactly **one** clear source citation link per response.
* **Footer:** Every response must end with: `“Last updated from sources: <date>”`.

### Refusal Handling
For any advisory, opinionated, or speculative query (e.g., *"Should I invest in this fund?"*, *"Which fund is better?"*):
* Refuse politely and clearly.
* Reinforce the facts-only limitation.
* Provide an educational link to a regulatory body (e.g., AMFI or SEBI resources).

---

## 4. User Interface (Minimalist & Premium)

A clean, user-friendly UI consisting of:
* A welcome message.
* Three clickable example questions to help users get started.
* A prominent, visible disclaimer: **“Facts-only. No investment advice.”**

---

## 5. Key Constraints & Guiding Rules

| Constraint Area | Rules & Guidelines |
| :--- | :--- |
| **Data Sources** | Use **only** official public sources (AMC, AMFI, SEBI). No third-party blogs, articles, or aggregators. |
| **Privacy & Security** | **Strictly prohibited** to collect, store, or process PII or credentials: PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers. |
| **Content Restrictions** | No investment advice, recommendations, performance comparisons, or return calculations. Performance-related queries must only redirect the user to the official factsheet. |
| **Transparency** | Answers must be short, highly factual, and verifiable, featuring a direct citation link and a last-updated footer. |

---

## 6. Expected Deliverables

* **FAQ Assistant Application:** RAG pipeline and Minimal UI.
* **README Document:**
  * Setup and run instructions.
  * Details of the selected AMC and schemes.
  * RAG architecture overview.
  * Known limitations.
  * The required disclaimer snippet: *“Facts-only. No investment advice.”*
