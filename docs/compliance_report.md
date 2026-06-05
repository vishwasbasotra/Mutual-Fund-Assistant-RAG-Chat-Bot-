# Phase 4 Compliance Verification & Audit Report

Executed on 50 factual test queries and 15 guardrail test cases.

## 1. Executive Summary

| Guardrail category | Total Tests | Passed | Success Rate |
| --- | --- | --- | --- |
| PII Leakage Interception | 5 | 5 | 100.0% |
| Advisory/Speculative Refusal | 5 | 5 | 100.0% |
| Ambiguity Clarification | 5 | 5 | 100.0% |
| Factual RAG Compliance (<= 3 sentences, citation, footer) | 50 | 50 | 100.0% |

## 2. Detailed Factual Test Results

| No. | Query | Status | Sentences | Citation | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | What is the exit load of HDFC Small Cap Fund? | **PASS** | 2 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 2 | What is the minimum investment for HDFC Small Cap Fund? | **PASS** | 2 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Small_Cap_Fund_June_2024.pdf` | Compliant |
| 3 | Which index does HDFC Mid-Cap Opportunities Fund track? | **PASS** | 2 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Mid-Cap_Opportunities_Fund_June_2024.pdf` | Compliant |
| 4 | What is the benchmark index of HDFC Top 100 Fund? | **PASS** | 2 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 5 | How to download consolidated account statement? | **PASS** | 3 | `https://www.hdfcfund.com/investor-services/consolidated-account-statement` | Compliant |
| 6 | Explain exit load for HDFC Multi Cap Fund. | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 7 | What is the minimum SIP for HDFC Mid-Cap Opportunities? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Mid-Cap_Opportunities_Fund_June_2024.pdf` | Compliant |
| 8 | What is the riskometer rating for HDFC Gold ETF Fund of Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 9 | What is the risk level of HDFC Top 100 Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 10 | Under what circumstances is exit load nil for HDFC Small Cap? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 11 | Explain NAV for HDFC Top 100 Fund | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 12 | What is the exit load of HDFC Top 100 Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` | Compliant |
| 13 | What is the minimum lumpsum amount for HDFC Multi Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 14 | What is the benchmark of HDFC Gold ETF Fund of Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 15 | What is the expense ratio or TER of HDFC Small Cap? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 16 | Who is the fund manager for HDFC Mid-Cap Opportunities Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Mid-Cap_Opportunities_Fund_June_2024.pdf` | Compliant |
| 17 | What is the asset size of HDFC Top 100 Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Large_Cap_Factsheet.pdf` | Compliant |
| 18 | How to download CAS through CDSL? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Gold_ETF_FOF_June_2024.pdf` | Compliant |
| 19 | Is there any exit load for HDFC Gold ETF FoF? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 20 | What is the inception date of HDFC Small Cap Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Small_Cap_Factsheet.pdf` | Compliant |
| 21 | What is the exit load for HDFC Multi Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 22 | What is the minimum additional purchase amount for HDFC Top 100? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 23 | Explain exit loads of HDFC Mid-Cap Opportunities. | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` | Compliant |
| 24 | What is the investment objective of HDFC Small Cap Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Small_Cap_Fund_June_2024.pdf` | Compliant |
| 25 | What is the minimum investment for HDFC Top 100 Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` | Compliant |
| 26 | Does HDFC Multi Cap Fund have an exit load? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 27 | What is the benchmark index for HDFC Small Cap? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 28 | Who manages the HDFC Top 100 Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 29 | What is the risk classification of HDFC Multi Cap Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Multi_Cap_Fund_June_2024.pdf` | Compliant |
| 30 | What is the minimum investment in HDFC Gold ETF Fund of Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 31 | How can I request my account statement from HDFC Mutual Fund? | **PASS** | 3 | `https://www.hdfcfund.com/investor-services/statement-request` | Compliant |
| 32 | What is the exit load of HDFC Gold ETF FoF if redeemed after 1 year? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 33 | What is the benchmark for HDFC Mid-Cap Opportunities? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` | Compliant |
| 34 | What is the risk profile of HDFC Mid-Cap Opportunities? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` | Compliant |
| 35 | Who is the fund manager of HDFC Multi Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 36 | What is the benchmark index of HDFC Multi Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` | Compliant |
| 37 | Explain minimum SIP amount for HDFC Gold ETF Fund of Fund. | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Gold_ETF_FOF_June_2024.pdf` | Compliant |
| 38 | What is the exit load structure of HDFC Small Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 39 | What is the entry load for HDFC Top 100 Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Large_Cap_Factsheet.pdf` | Compliant |
| 40 | Is there an entry load for HDFC Small Cap Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 41 | What is the exit load of HDFC Top 100 Fund direct plan? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` | Compliant |
| 42 | How to get mutual fund statement by email? | **PASS** | 3 | `https://www.hdfcfund.com/investor-services/statement-request` | Compliant |
| 43 | How to download capital gains statement from HDFC Mutual Fund? | **PASS** | 3 | `https://www.hdfcfund.com/investor-services/statement-request` | Compliant |
| 44 | What is the benchmark of HDFC Top 100 Fund? | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf` | Compliant |
| 45 | Who is the fund manager of HDFC Gold ETF Fund of Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` | Compliant |
| 46 | What is the riskometer of HDFC Small Cap? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
| 47 | Explain the exit load for redemption within 12 months for HDFC Multi Cap. | **PASS** | 3 | `https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Multi_Cap_Fund_June_2024.pdf` | Compliant |
| 48 | What is the minimum application size for HDFC Mid-Cap Opportunities Fund? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` | Compliant |
| 49 | How do I check my CAS statement online? | **PASS** | 3 | `https://www.hdfcfund.com/investor-services/consolidated-account-statement` | Compliant |
| 50 | What is the benchmark index of HDFC Small Cap Fund direct growth? | **PASS** | 3 | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` | Compliant |
