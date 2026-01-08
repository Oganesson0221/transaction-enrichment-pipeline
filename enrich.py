import pandas as pd
import numpy as np
from typing import Dict, Any, List, Callable

from schema import EnrichedTransactionSchema
from rules import (
    rule_tax_related,
    rule_specific_merchant,
    rule_payment_rail,
    rule_ecommerce_purchase,
    rule_credit_card_payment,
    rule_fallback
)

# Data-driven rule orchestration: Define a single ordered RULES list
# Priority Order (highest -> lowest)
RULES: List[Callable[[str, float], Any]] = [
    rule_tax_related,
    rule_specific_merchant,
    rule_payment_rail,
    rule_ecommerce_purchase,
    rule_credit_card_payment,
]

def enrich_transaction_record(row) -> EnrichedTransactionSchema:
    description = str(row['Description'])
    amount_usd = row['AmountUSD']

    enriched_data: EnrichedTransactionSchema = {}

    # Orchestrator owns routing + metadata only
    # Iterate over rules in order, first non-None result wins
    for rule_func in RULES:
        result = rule_func(description, amount_usd)
        if result:
            fields, confidence, rule_id = result
            enriched_data.update(fields)
            enriched_data["Confidence"] = confidence
            enriched_data["RuleHit"] = rule_id
            return enriched_data

    # Use fallback rule only if no rules match
    fields, confidence, rule_id = rule_fallback(description, amount_usd)
    enriched_data.update(fields)
    enriched_data["Confidence"] = confidence
    enriched_data["RuleHit"] = rule_id
    return enriched_data

def enrich_transactions(input_file: str, output_file: str):
    df = pd.read_excel(input_file)

    enriched_df = df.apply(enrich_transaction_record, axis=1, result_type='expand')

    # Strict schema enforcement: Assert at runtime that enriched output contains exactly the keys
    # defined in EnrichedTransactionSchema
    expected_columns = set(EnrichedTransactionSchema.__annotations__.keys())
    actual_columns = set(enriched_df.columns)

    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    if missing_columns or extra_columns:
        error_message = f"Schema enforcement failed: "
        if missing_columns:
            error_message += f"Missing columns: {missing_columns}. "
        if extra_columns:
            error_message += f"Extra columns: {extra_columns}."
        raise ValueError(error_message)

    # Ensure columns are in the correct order as per schema
    enriched_df = enriched_df[list(EnrichedTransactionSchema.__annotations__.keys())]

    # Original columns that are not part of the schema (e.g., TransactionDate, AmountUSD from preprocess.py)
    # should be preserved if they are not overwritten by enrichment.
    # The previous enrichment output did not keep these, so I will ensure only the enriched columns are in the final output.
    df = enriched_df

    df.to_excel(output_file, index=False)
    print(f"Enriched data written to {output_file}")

if __name__ == "__main__":
    input_excel_file = "data/processed/transactions_cleaned.xlsx"
    output_excel_file = "data/processed/transactions_enriched.xlsx"
    enrich_transactions(input_excel_file, output_excel_file)
