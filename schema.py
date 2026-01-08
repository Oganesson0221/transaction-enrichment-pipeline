from typing import TypedDict

class EnrichedTransactionSchema(TypedDict):
    TransactionClassification: str
    MerchantClassification: str
    NormalizedEntity: str
    TransactionName: str
    IsCreditCardExpense: bool
    Reason: str
    Confidence: float
    RuleHit: str

