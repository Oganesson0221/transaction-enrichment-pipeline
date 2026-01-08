import pandas as pd
from typing import Optional

def run_gap_analysis(input_file: str, output_report_file: Optional[str] = None, top_n: int = 10):
    df = pd.read_excel(input_file)

    print("\n--- Gap Analysis Report ---")

    # 1. % of transactions hitting each RuleHit
    rule_hit_distribution = df['RuleHit'].value_counts(normalize=True) * 100
    print("\n1. Distribution of Rule Hits (%):")
    print(rule_hit_distribution.to_string())

    # 2. % of transactions hitting RULE_FALLBACK
    fallback_percentage = rule_hit_distribution.get('RULE_FALLBACK', 0)
    print(f"\n2. Percentage of transactions hitting RULE_FALLBACK: {fallback_percentage:.2f}%")

    # 3. Top N most common descriptions in fallback
    fallback_df = df[df['RuleHit'] == 'RULE_FALLBACK']
    if not fallback_df.empty:
        top_fallback_descriptions = fallback_df['Description'].value_counts().head(top_n)
        print(f"\n3. Top {top_n} most common descriptions in Fallback transactions:")
        print(top_fallback_descriptions.to_string())
    else:
        print("\n3. No fallback transactions to analyze descriptions.")

    # 4. Distribution of TransactionClassification
    transaction_classification_distribution = df['TransactionClassification'].value_counts(normalize=True) * 100
    print("\n4. Distribution of Transaction Classifications (%):")
    print(transaction_classification_distribution.to_string())

    # 5. Average confidence per rule
    avg_confidence_per_rule = df.groupby('RuleHit')['Confidence'].mean()
    print("\n5. Average Confidence per Rule:")
    print(avg_confidence_per_rule.to_string())

    # Error surfacing: High-frequency fallback descriptions and sample rows
    print("\n--- Actionable Signals for RAG / ML Improvements ---")
    if not fallback_df.empty:
        print("\nHigh-frequency fallback descriptions (consider for new rules or RAG training):")
        for desc, count in top_fallback_descriptions.items():
            print(f"- '{desc}' (count: {count})")

        print("\nSample Fallback Transactions for Manual Inspection:")
        print(fallback_df.sample(min(5, len(fallback_df)))[['Description', 'AmountUSD', 'TransactionClassification', 'Reason', 'Confidence', 'RuleHit']].to_string())

        if output_report_file:
            fallback_df.to_csv(output_report_file, index=False)
            print(f"\nOptional CSV report for fallback transactions written to {output_report_file}")
    else:
        print("\nNo fallback transactions to provide actionable signals.")

    print("\n--- Gap Analysis Complete ---")

if __name__ == "__main__":
    input_excel_file = "data/processed/transactions_enriched.xlsx"
    output_csv_report = "data/processed/fallback_transactions_report.csv" # Optional report

    run_gap_analysis(input_excel_file, output_csv_report)

