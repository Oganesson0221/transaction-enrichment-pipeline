import pandas as pd
import numpy as np
from typing import Dict, Any

from schema import EnrichedTransactionSchema
from rules import (
    rule_tax_related,
    rule_specific_merchant,
    rule_payment_rail,
    rule_ecommerce_purchase,
    rule_credit_card_payment,
    rule_fallback
)

def enrich_transaction_record(row) -> EnrichedTransactionSchema:
    description = str(row['Description'])
    amount_usd = row['AmountUSD']

    # Initialize with fallback values
    enriched_data: EnrichedTransactionSchema = {
        "TransactionClassification": "Other",
        "MerchantClassification": "Other",
        "NormalizedEntity": "Other",
        "TransactionName": description,
        "IsCreditCardExpense": False,
        "Reason": "Fallback",
        "Confidence": 0.0,
        "RuleHit": "RULE_FALLBACK"
    }

    # Apply rules in priority order (first match wins)
    # Tax-related rules (highest confidence)
    result = rule_tax_related(description, amount_usd)
    if result:
        fields, confidence, rule_id = result
        enriched_data.update(fields)
        enriched_data["Confidence"] = confidence
        enriched_data["RuleHit"] = rule_id
        enriched_data["Reason"] = "Tax-related transaction detected."
        return enriched_data

    # Specific merchant rules
    result = rule_specific_merchant(description, amount_usd)
    if result:
        fields, confidence, rule_id = result
        enriched_data.update(fields)
        enriched_data["Confidence"] = confidence
        enriched_data["RuleHit"] = rule_id
        enriched_data["Reason"] = f"Match found for specific merchant: {fields['MerchantClassification']}"
        return enriched_data

    # Payment rail rules
    result = rule_payment_rail(description, amount_usd)
    if result:
        fields, confidence, rule_id = result
        enriched_data.update(fields)
        enriched_data["Confidence"] = confidence
        enriched_data["RuleHit"] = rule_id
        enriched_data["Reason"] = "Payment rail keyword detected."
        return enriched_data

    # General semantic rules
    result = rule_ecommerce_purchase(description, amount_usd)
    if result:
        fields, confidence, rule_id = result
        enriched_data.update(fields)
        enriched_data["Confidence"] = confidence
        enriched_data["RuleHit"] = rule_id
        enriched_data["Reason"] = "Ecommerce purchase identified."
        return enriched_data

    result = rule_credit_card_payment(description, amount_usd)
    if result:
        fields, confidence, rule_id = result
        enriched_data.update(fields)
        enriched_data["Confidence"] = confidence
        enriched_data["RuleHit"] = rule_id
        enriched_data["Reason"] = "Credit card payment identified."
        return enriched_data

    # Fallback rule
    fields, confidence, rule_id = rule_fallback(description, amount_usd)
    enriched_data.update(fields)
    enriched_data["Confidence"] = confidence
    enriched_data["RuleHit"] = rule_id
    enriched_data["Reason"] = "No specific rule matched; defaulted to fallback."
    return enriched_data

def enrich_transactions(input_file: str, output_file: str):
    df = pd.read_excel(input_file)

    enriched_df = df.apply(enrich_transaction_record, axis=1, result_type='expand')

    # Merge the original DataFrame with the enriched columns
    df = pd.concat([df.drop(columns=list(EnrichedTransactionSchema.__annotations__.keys()), errors='ignore'), enriched_df], axis=1)

    # Ensure all schema columns are present and in the correct order
    final_columns = list(EnrichedTransactionSchema.__annotations__.keys())
    df = df[final_columns + [col for col in df.columns if col not in final_columns]]

    df.to_excel(output_file, index=False)
    print(f"Enriched data written to {output_file}")

if __name__ == "__main__":
    input_excel_file = "data/processed/transactions_cleaned.xlsx"
    output_excel_file = "data/processed/transactions_enriched.xlsx"
    enrich_transactions(input_excel_file, output_excel_file)
