import re
from typing import Dict, Any, Optional, Tuple

# Lookup Maps
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

# Helper function for keyword presence
def is_keyword_present(text: str, keywords: list[str]) -> bool:
    return any(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE) for keyword in keywords)

# Rule Functions
def rule_tax_related(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    if is_keyword_present(description, TAX_KEYWORDS):
        return {
            "TransactionClassification": "Tax Related",
            "MerchantClassification": "Tax Authority",
            "NormalizedEntity": "Tax Authority",
            "TransactionName": description,
            "IsCreditCardExpense": False,
            "Reason": "Tax-related transaction detected."
        }, 1.0, "RULE_TAX_KEYWORD"
    return None

def rule_specific_merchant(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    merchant = None
    description_lower = description.lower()
    for keyword, merchant_name in MERCHANT_LOOKUP.items():
        if keyword in description_lower:
            merchant = merchant_name
            break

    if merchant:
        return {
            "TransactionClassification": "Merchant Payment",
            "MerchantClassification": merchant,
            "NormalizedEntity": merchant,
            "TransactionName": description,
            "IsCreditCardExpense": False,
            "Reason": f"Match found for specific merchant: {merchant}"
        }, 0.9, "RULE_MERCHANT_LOOKUP"
    return None

def rule_payment_rail(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    if is_keyword_present(description, PAYMENT_RAIL_KEYWORDS):
        return {
            "TransactionClassification": "Payment Rail Transaction",
            "MerchantClassification": "Payment Processor",
            "NormalizedEntity": "Payment Processor",
            "TransactionName": description,
            "IsCreditCardExpense": False,
            "Reason": "Payment rail keyword detected."
        }, 0.8, "RULE_PAYMENT_RAIL"
    return None

def rule_ecommerce_purchase(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    if amount_usd > 0 and ("marketplace" in description.lower() or "ecommerce" in description.lower()):
        return {
            "TransactionClassification": "Ecommerce Purchase",
            "MerchantClassification": "Online Marketplace",
            "NormalizedEntity": "Online Marketplace",
            "TransactionName": description,
            "IsCreditCardExpense": False,
            "Reason": "Ecommerce purchase identified."
        }, 0.7, "RULE_ECOMMERCE_PURCHASE"
    return None

def rule_credit_card_payment(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    if amount_usd < 0 and ("loan" in description.lower() or "payment" in description.lower() or "credit card" in description.lower()):
        return {
            "TransactionClassification": "Credit Card Payment",
            "MerchantClassification": "Credit Card Company",
            "NormalizedEntity": "Credit Card Company",
            "TransactionName": description,
            "IsCreditCardExpense": True,
            "Reason": "Credit card payment identified."
        }, 0.7, "RULE_CREDIT_CARD_PAYMENT"
    return None

def rule_fallback(
    description: str,
    amount_usd: float
) -> Tuple[Dict[str, Any], float, str]:
    return {
        "TransactionClassification": "Other",
        "MerchantClassification": "Other",
        "NormalizedEntity": "Other",
        "TransactionName": description,
        "IsCreditCardExpense": False,
        "Reason": "No specific rule matched; defaulted to fallback."
    }, 0.1, "RULE_FALLBACK"
