import re
from typing import Dict, Any, Optional, Tuple, List

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

KB_MERCHANTS: List[Dict[str, Any]] = [
    {
        "surface_forms": ["shoppay", "shopify", "shop pay"],
        "normalized_entity": "Shopify",
        "transaction_classification": "Ecommerce Platform Fee",
        "explanation": "Transaction related to Shopify e-commerce platform."
    },
    {
        "surface_forms": ["tiktok inc", "tiktok shop"],
        "normalized_entity": "TikTok",
        "transaction_classification": "Social Media Advertising",
        "explanation": "Transaction related to TikTok advertising or shopping."
    },
    {
        "surface_forms": ["paychex"],
        "normalized_entity": "Paychex",
        "transaction_classification": "Payroll Service",
        "explanation": "Transaction for payroll services provided by Paychex."
    },
    {
        "surface_forms": ["mbfs.com"],
        "normalized_entity": "MBFS",
        "transaction_classification": "Financial Service",
        "explanation": "Transaction related to MBFS financial services."
    },
    {
        "surface_forms": ["global - e", "global-e"],
        "normalized_entity": "Global-e",
        "transaction_classification": "Cross-Border Ecommerce",
        "explanation": "Transaction related to Global-e cross-border e-commerce solutions."
    },
    {
        "surface_forms": ["wayflyer"],
        "normalized_entity": "Wayflyer",
        "transaction_classification": "Revenue-Based Financing",
        "explanation": "Transaction related to Wayflyer revenue-based financing."
    },
    {
        "surface_forms": ["walmart"],
        "normalized_entity": "Walmart",
        "transaction_classification": "Retail Purchase",
        "explanation": "Retail purchase at Walmart."
    }
]

def is_keyword_present(text: str, keywords: list[str]) -> bool:
    return any(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE) for keyword in keywords)

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

def rule_rag_fallback(
    description: str,
    amount_usd: float
) -> Optional[Tuple[Dict[str, Any], float, str]]:
    description_lower = description.lower()
    for entry in KB_MERCHANTS:
        for surface_form in entry["surface_forms"]:
            if surface_form in description_lower:
                return {
                    "TransactionClassification": entry["transaction_classification"],
                    "MerchantClassification": entry["normalized_entity"],
                    "NormalizedEntity": entry["normalized_entity"],
                    "TransactionName": description,
                    "IsCreditCardExpense": False,
                    "Reason": f"RAG match based on: {surface_form} - {entry['explanation']}"
                }, 0.6, "RULE_RAG_FALLBACK"
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
