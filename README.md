# transaction-enrichment-pipeline

## Gap Analysis Results

The `gap_analysis.py` script evaluates the performance of the rule-based enrichment pipeline, identifying areas where the current rules are not sufficient and providing actionable signals for future RAG/ML improvements.

### Summary Metrics

**1. Distribution of Rule Hits (%):**
```
RuleHit
RULE_FALLBACK               63.412884
RULE_PAYMENT_RAIL           19.038220
RULE_MERCHANT_LOOKUP        15.826305
RULE_TAX_KEYWORD             1.184281
RULE_CREDIT_CARD_PAYMENT     0.538310
```

**2. Percentage of transactions hitting RULE_FALLBACK: 63.41%**

**3. Top 10 most common descriptions in Fallback transactions:**
```
Description
electronic deposit shoppayinst afrm    909
electronic deposit shopify             596
electronic deposit tiktok inc          293
paychex                                214
electronic withdrawal mbfs.com          56
electronic deposit global - e           48
electronic deposit tiktok shop          48
electronic withdrawal wayflyer          41
mobile check deposit                    38
walmart                                 25
```

**4. Distribution of Transaction Classifications (%):**
```
TransactionClassification
Other                       63.412884
Payment Rail Transaction    19.038220
Merchant Payment            15.826305
Tax Related                  1.184281
Credit Card Payment          0.538310
```

**5. Average Confidence per Rule:**
```
RuleHit
RULE_CREDIT_CARD_PAYMENT    0.7
RULE_FALLBACK               0.1
RULE_MERCHANT_LOOKUP        0.9
RULE_PAYMENT_RAIL           0.8
RULE_TAX_KEYWORD            1.0
```

### Actionable Signals for RAG / ML Improvements

**High-frequency fallback descriptions (consider for new rules or RAG training):**
- 'electronic deposit shoppayinst afrm' (count: 909)
- 'electronic deposit shopify' (count: 596)
- 'electronic deposit tiktok inc' (count: 293)
- 'paychex' (count: 214)
- 'electronic withdrawal mbfs.com' (count: 56)
- 'electronic deposit global - e' (count: 48)
- 'electronic deposit tiktok shop' (count: 48)
- 'electronic withdrawal wayflyer' (count: 41)
- 'mobile check deposit' (count: 38)
- 'walmart' (count: 25)

An optional CSV report for fallback transactions has been generated and can be found at `data/processed/fallback_transactions_report.csv`.
