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
    rule_rag_fallback,
    rule_fallback
)

RULES: List[Callable[[str, float], Any]] = [
    rule_tax_related,
    rule_specific_merchant,
    rule_payment_rail,
    rule_ecommerce_purchase,
    rule_credit_card_payment,
    rule_rag_fallback,
]

def enrich_transaction_record(row) -> EnrichedTransactionSchema:
    description = str(row['Description'])
    amount_usd = row['AmountUSD']

    enriched_data: EnrichedTransactionSchema = {}

    for rule_func in RULES:
        result = rule_func(description, amount_usd)
        if result:
            fields, confidence, rule_id = result
            enriched_data.update(fields)
            enriched_data["Confidence"] = confidence
            enriched_data["RuleHit"] = rule_id
            return enriched_data

    fields, confidence, rule_id = rule_fallback(description, amount_usd)
    enriched_data.update(fields)
    enriched_data["Confidence"] = confidence
    enriched_data["RuleHit"] = rule_id
    return enriched_data

def enrich_transactions(input_file: str = None, output_file: str = None, df: pd.DataFrame = None):
    """
    Enrich transactions from either an Excel file or a DataFrame.
    
    Args:
        input_file: Path to Excel file (used when processing files)
        output_file: Path to output Excel file (optional)
        df: DataFrame to process directly (used by API)
    
    Returns:
        Enriched DataFrame
    """
    if df is None:
        df = pd.read_excel(input_file)

    enriched_df = df.apply(enrich_transaction_record, axis=1, result_type='expand')

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

    enriched_df = enriched_df[list(EnrichedTransactionSchema.__annotations__.keys())]

    original_preserved_columns = ['TransactionDate', 'Description', 'Category', 'AmountUSD', 'Balance']
    
    final_output_df = pd.concat([df[original_preserved_columns], enriched_df], axis=1)
    
    all_expected_columns_ordered = original_preserved_columns + [col for col in list(EnrichedTransactionSchema.__annotations__.keys()) if col not in original_preserved_columns]
    
    result_df = final_output_df[all_expected_columns_ordered]

    if output_file:
        result_df.to_excel(output_file, index=False)
        print(f"Enriched data written to {output_file}")
    
    return result_df

if __name__ == "__main__":
    input_excel_file = "data/processed/transactions_cleaned.xlsx"
    output_excel_file = "data/processed/transactions_enriched.xlsx"
    enrich_transactions(input_excel_file, output_excel_file)
