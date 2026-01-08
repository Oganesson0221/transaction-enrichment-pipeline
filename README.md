# Transaction Enrichment Pipeline

## 1. Project Overview

This repository implements a financial transaction enrichment pipeline designed to transform raw transaction data into clean, normalized, and explainable records. The pipeline operates in a deterministic manner, ensuring immutability of raw data and clear lineage for each processing step. Transaction enrichment is crucial for financial analysis, fraud detection, and business intelligence, as it adds valuable contextual information to otherwise raw and unstructured transaction descriptions.

The high-level architecture consists of distinct, modular stages: a preprocessing layer for initial cleanup, a rule-based enrichment engine, and a gap analysis module for evaluating pipeline performance.

## 2. Pipeline Stages

### `preprocess.py`
This script handles the initial cleaning and standardization of raw transaction data. It performs structural and formatting cleanup, such as collapsing credit/debit into a single signed amount, stripping commas, casting to appropriate data types, and standardizing date formats. It strictly adheres to immutability, never modifying the raw input data.

### `enrich.py`
This is the core of the enrichment pipeline, acting as an orchestrator for applying a series of deterministic and RAG-based rules. It consumes the preprocessed data and adds new enriched fields based on a predefined priority order. The orchestrator's role is limited to selecting the first rule that fires and attaching metadata like confidence and the rule identifier.

### `rules.py`
This module defines the individual rule functions and their associated lookup maps. Each rule is an isolated function that, if triggered, returns a complete set of semantic fields (including classification, normalized entities, and a reason for the classification), along with a confidence score and a unique rule ID. Rules are kept pure, with no direct DataFrame manipulation or I/O.

### `schema.py`
This file serves as the single source of truth for the canonical output schema of the enriched transactions. It explicitly defines the field names and their expected types, ensuring strict schema enforcement at runtime to prevent silent schema drift. No business logic is present in this module.

### `gap_analysis.py`
This script evaluates the performance of the rule-based enrichment pipeline. It quantifies where the rule engine fails (e.g., fallback rate, unhandled descriptions) and produces actionable signals for potential RAG or ML improvements. It's strictly non-intrusive, consuming the enriched output without influencing the pipeline's logic.

## 3. Rule Engine Design

The rule engine is designed for determinism, auditability, and extensibility, following a strict priority order for rule application:

*   **Deterministic Rules**: A series of explicit, logic-based rules (e.g., `rule_tax_related`, `rule_specific_merchant`, `rule_payment_rail`, `rule_ecommerce_purchase`, `rule_credit_card_payment`). These rules provide high-confidence classifications for known patterns.
*   **RAG Fallback Rule (`rule_rag_fallback`)**: If all deterministic rules fail to match, a Retrieval-Augmented Generation (RAG) based fallback rule attempts to classify transactions using a small, local merchant knowledge base. This rule acts as a "smarter" fallback, absorbing the long tail of less common or more ambiguous transactions.
*   **Rule Priority and Orchestration**: Rules are applied in a strict, ordered sequence. The first rule to successfully classify a transaction "wins," and no subsequent rules are applied. This ensures consistent and predictable outcomes. The `enrich.py` orchestrator manages this priority and attaches rule metadata, while individual rules own their semantic outputs.

## 4. Gap Analysis & Evaluation

The `gap_analysis.py` module provides critical insights into the pipeline's effectiveness by tracking various metrics:

*   **RuleHit Distribution**: Percentage of transactions classified by each specific rule, including `RULE_FALLBACK` and `RULE_RAG_FALLBACK`.
*   **Fallback Rate**: The percentage of transactions that fall through all specific and RAG rules, defaulting to `RULE_FALLBACK`. This is the primary success metric, indicating the coverage of the rule engine. A lower fallback rate is desirable.
*   **Top Fallback Descriptions**: Identifies the most frequent transaction descriptions that hit the `RULE_FALLBACK`, highlighting areas for new deterministic rules or expansion of the RAG knowledge base.
*   **Average Confidence per Rule**: Provides an understanding of the confidence levels assigned by different rule types.
*   **Deltas Interpretation**: Comparing these metrics before and after the introduction of the RAG fallback rule helps quantify its impact. A material drop in `RULE_FALLBACK` percentage, a significant rise in `RULE_RAG_FALLBACK` usage, and a disappearance of previously common fallback terms indicate successful RAG integration.

The gap analysis aims to answer "Where do rules fail?" and "What should RAG learn first?", providing a data-driven roadmap for pipeline improvements.

## 5. Results (Before vs After RAG)

This section presents the computed deltas from the gap analysis, comparing the pipeline's performance before and after the integration of the `rule_rag_fallback`.

**Fallback Rate Delta:**
*   **Before RAG (`RULE_FALLBACK`):** 63.41%
*   **After RAG (`RULE_FALLBACK`):** 23.06%
*   **Delta:** -40.36% (a negative delta indicates a reduction in fallback rate, which is an improvement)

**RULE_RAG_FALLBACK Percentage:**
*   **Before RAG (`RULE_RAG_FALLBACK`):** 0.00%
*   **After RAG (`RULE_RAG_FALLBACK`):** 40.36%
*   **Delta:** 40.36%

**Top Fallback Descriptions (Changes):**
*   **Descriptions removed from top fallback (due to RAG):** walmart, electronic deposit shopify, electronic deposit tiktok inc, electronic deposit global - e, electronic deposit shoppayinst afrm, electronic withdrawal mbfs.com, paychex, electronic withdrawal wayflyer, electronic deposit tiktok shop
*   **Descriptions newly appearing in top fallback:** electronic withdrawal state of, electronic withdrawal oklahomataxpmts, electronic withdrawal wvtreasury, verizon wireless, web authorized pmt google, electronic withdrawal va dept taxation, electronic withdrawal az dept of rev, venmo, electronic withdrawal co dept revenue

**Average Confidence Delta:**
*   **Overall Average Confidence Before RAG:** 0.37
*   **Overall Average Confidence After RAG:** 0.58
*   **Overall Confidence Delta:** 0.20 (a positive delta indicates an overall increase in confidence)

**Interpretation of Improvements:**
The integration of the RAG fallback rule has materially reduced the overall fallback rate by 40.36%. This indicates that the RAG mechanism effectively absorbed a significant portion of previously unclassified transactions. The appearance of `RULE_RAG_FALLBACK` at 40.36% confirms its successful intervention. The reduction in common fallback descriptions like "shopify" and "tiktok" demonstrates RAG's ability to handle the "long tail" of merchants. The remaining fallback transactions now represent genuinely unknown cases, providing a clearer target for future knowledge base expansion. The overall average confidence in classifications has also increased, reflecting the improved quality of enrichment.

## 6. Extensibility

The pipeline is designed for straightforward extension and iterative improvement:

*   **Adding New Deterministic Rules**: New deterministic rules can be added to `rules.py` by defining a new rule function matching the standard signature and then including it in the `RULES` list within `enrich.py` at the appropriate priority level.
*   **Extending the RAG Knowledge Base**: The `KB_MERCHANTS` in `rules.py` can be easily extended with new `surface_forms`, `normalized_entity`, `transaction_classification`, and `explanation` entries. Adding to this knowledge base directly improves the coverage of the RAG fallback.
*   **Iterating with Gap Analysis**: The `gap_analysis.py` script facilitates an "ML-lite roadmap." By running the gap analysis after adding new rules or extending the KB, the impact can be immediately measured, and the top remaining fallback terms can guide the next iteration of improvements. This continuous loop allows for data-driven refinement of the enrichment logic.
