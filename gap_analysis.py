import pandas as pd
import json
from typing import Optional, Dict, Any, List

def _compute_single_report_metrics(df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    metrics = {}

    metrics["rule_hit_distribution"] = (df['RuleHit'].value_counts(normalize=True) * 100).to_dict()
    metrics["fallback_percentage"] = metrics["rule_hit_distribution"].get('RULE_FALLBACK', 0.0)

    fallback_df = df[df['RuleHit'] == 'RULE_FALLBACK']
    if not fallback_df.empty:
        metrics["top_fallback_descriptions"] = fallback_df['Description'].value_counts().head(top_n).to_dict()
    else:
        metrics["top_fallback_descriptions"] = {}

    metrics["transaction_classification_distribution"] = (df['TransactionClassification'].value_counts(normalize=True) * 100).to_dict()
    metrics["avg_confidence_per_rule"] = df.groupby('RuleHit')['Confidence'].mean().to_dict()
    metrics["avg_overall_confidence"] = df['Confidence'].mean()
    
    return metrics

def compare_gap_analysis(
    baseline_file: str,
    post_rag_file: str,
    output_deltas_file: str,
    top_n: int = 10
):
    df_baseline = pd.read_excel(baseline_file)
    df_post_rag = pd.read_excel(post_rag_file)

    metrics_baseline = _compute_single_report_metrics(df_baseline, top_n)
    metrics_post_rag = _compute_single_report_metrics(df_post_rag, top_n)

    deltas: Dict[str, Any] = {}

    # Fallback rate delta
    deltas["fallback_percentage_delta"] = metrics_post_rag["fallback_percentage"] - metrics_baseline["fallback_percentage"]
    deltas["baseline_fallback_percentage"] = metrics_baseline["fallback_percentage"]
    deltas["post_rag_fallback_percentage"] = metrics_post_rag["fallback_percentage"]

    # RULE_RAG_FALLBACK percentage delta
    baseline_rag_fallback = metrics_baseline["rule_hit_distribution"].get('RULE_RAG_FALLBACK', 0.0)
    post_rag_rag_fallback = metrics_post_rag["rule_hit_distribution"].get('RULE_RAG_FALLBACK', 0.0)
    deltas["rag_fallback_percentage_delta"] = post_rag_rag_fallback - baseline_rag_fallback
    deltas["baseline_rag_fallback_percentage"] = baseline_rag_fallback
    deltas["post_rag_rag_fallback_percentage"] = post_rag_rag_fallback

    # Top fallback descriptions (added / removed / changed)
    baseline_top_fallback = set(metrics_baseline["top_fallback_descriptions"].keys())
    post_rag_top_fallback = set(metrics_post_rag["top_fallback_descriptions"].keys())
    deltas["fallback_descriptions_added"] = list(post_rag_top_fallback - baseline_top_fallback)
    deltas["fallback_descriptions_removed"] = list(baseline_top_fallback - post_rag_top_fallback)
    deltas["baseline_top_fallback_descriptions"] = metrics_baseline["top_fallback_descriptions"]
    deltas["post_rag_top_fallback_descriptions"] = metrics_post_rag["top_fallback_descriptions"]

    # Average confidence per rule deltas
    avg_confidence_deltas = {}
    all_rules = set(metrics_baseline["avg_confidence_per_rule"].keys()).union(set(metrics_post_rag["avg_confidence_per_rule"].keys()))
    for rule in all_rules:
        baseline_conf = metrics_baseline["avg_confidence_per_rule"].get(rule, 0.0)
        post_rag_conf = metrics_post_rag["avg_confidence_per_rule"].get(rule, 0.0)
        avg_confidence_deltas[rule] = post_rag_conf - baseline_conf
    deltas["avg_confidence_per_rule_deltas"] = avg_confidence_deltas
    deltas["baseline_avg_confidence_per_rule"] = metrics_baseline["avg_confidence_per_rule"]
    deltas["post_rag_avg_confidence_per_rule"] = metrics_post_rag["avg_confidence_per_rule"]

    # Overall average confidence delta
    deltas["overall_avg_confidence_delta"] = metrics_post_rag["avg_overall_confidence"] - metrics_baseline["avg_overall_confidence"]
    deltas["baseline_overall_avg_confidence"] = metrics_baseline["avg_overall_confidence"]
    deltas["post_rag_overall_avg_confidence"] = metrics_post_rag["avg_overall_confidence"]

    # Persist results to JSON
    with open(output_deltas_file, 'w') as f:
        json.dump(deltas, f, indent=4)

    print(f"Gap analysis deltas computed and saved to {output_deltas_file}")

if __name__ == "__main__":
    baseline_enriched_file = "data/processed/baseline_enriched.xlsx"
    post_rag_enriched_file = "data/processed/post_rag_enriched.xlsx"
    output_deltas_file = "data/processed/gap_analysis_deltas.json"

    compare_gap_analysis(baseline_enriched_file, post_rag_enriched_file, output_deltas_file)
