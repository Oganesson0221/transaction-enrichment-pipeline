import pandas as pd
import numpy as np
import re

MERCHANT_LOOKUP = {
    "capital one": "Capital One",
    "shopify capital": "Shopify Capital",
    "amazon": "Amazon",
    "starbucks": "Starbucks",
    "netflix": "Netflix",
}

TAX_KEYWORDS = [
    "tax", "irs", "hmrc", "revenue service"
]

PAYMENT_RAIL_KEYWORDS = [
    "visa", "zelle", "paypal", "afterpay", "mastercard", "amex", "square", "stripe"
]

def is_keyword_present(text, keywords):
    return any(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE) for keyword in keywords)

def extract_merchant(description):
    description_lower = description.lower()
    for keyword, merchant_name in MERCHANT_LOOKUP.items():
        if keyword in description_lower:
            return merchant_name
    return None

def classify_transaction(row):
    description = str(row['Description'])
    amount_usd = row['AmountUSD']

    transaction_classification = "Other"
    merchant_classification = "Other"
    normalized_entity = "Other"
    transaction_name = description
    is_credit_card_expense = False
    reason = "Fallback"

    if is_keyword_present(description, TAX_KEYWORDS):
        transaction_classification = "Tax Related"
        reason = "Tax Related Rule"
    else:
        merchant = extract_merchant(description)
        if merchant:
            merchant_classification = merchant
            normalized_entity = merchant
            transaction_classification = "Merchant Payment"
            reason = f"Specific Merchant Rule: {merchant}"

        elif is_keyword_present(description, PAYMENT_RAIL_KEYWORDS):
            transaction_classification = "Payment Rail Transaction"
            reason = "Payment Rail Rule"

        elif amount_usd > 0 and ("marketplace" in description.lower() or "ecommerce" in description.lower()):
            transaction_classification = "Ecommerce Purchase"
            reason = "General Semantic Rule: Ecommerce"

        elif amount_usd < 0 and ("loan" in description.lower() or "payment" in description.lower() or "credit card" in description.lower()):
            transaction_classification = "Credit Card Payment"
            is_credit_card_expense = True
            reason = "General Semantic Rule: Credit Card Payment"

    return pd.Series([
        transaction_classification,
        merchant_classification,
        normalized_entity,
        transaction_name,
        is_credit_card_expense,
        reason
    ], index=[
        'TransactionClassification',
        'MerchantClassification',
        'NormalizedEntity',
        'TransactionName',
        'IsCreditCardExpense',
        'Reason'
    ])

def enrich_transactions(input_file: str, output_file: str):
    df = pd.read_excel(input_file)

    df[[
        'TransactionClassification',
        'MerchantClassification',
        'NormalizedEntity',
        'TransactionName',
        'IsCreditCardExpense',
        'Reason'
    ]] = df.apply(classify_transaction, axis=1)

    df.to_excel(output_file, index=False)
    print(f"Enriched data written to {output_file}")

if __name__ == "__main__":
    input_excel_file = "data/processed/transactions_cleaned.xlsx"
    output_excel_file = "data/processed/transactions_enriched.xlsx"
    enrich_transactions(input_excel_file, output_excel_file)
