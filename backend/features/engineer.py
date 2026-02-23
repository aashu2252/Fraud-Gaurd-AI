"""
Feature Engineering Module — The "Inventive Step"

This module transforms raw behavioral transaction data into
fraud-signal features used by the XGBoost model.
"""
from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timezone
from collections import defaultdict


def return_to_purchase_ratio(history: List[Dict[str, Any]]) -> float:
    """
    Core fraud signal: ratio of return requests to total purchases.
    Normal shoppers: < 0.2. Wardrobers / fraudsters: often > 0.6.
    """
    purchases = sum(1 for t in history if t["action_type"] == "Purchase")
    returns = sum(1 for t in history if t["action_type"] == "ReturnRequest")
    if purchases == 0:
        return 0.0
    return round(returns / purchases, 4)


def temporal_gap_score(history: List[Dict[str, Any]]) -> float:
    """
    Average number of days between delivery and return request.
    Fraudsters tend to return items very quickly (1-3 days) after
    using/wearing them (compared to genuine returns at 7-15+ days).
    Returns a normalized score where LOWER = higher fraud risk.
    """
    gaps = []
    for t in history:
        if t["action_type"] == "ReturnRequest" and t.get("delivery_date") and t.get("return_date"):
            delivery = t["delivery_date"]
            returned = t["return_date"]
            if isinstance(delivery, str):
                delivery = datetime.fromisoformat(delivery)
            if isinstance(returned, str):
                returned = datetime.fromisoformat(returned)
            gap_days = max(0, (returned - delivery).days)
            gaps.append(gap_days)
    if not gaps:
        return 30.0  # Neutral: no returns recorded
    return round(sum(gaps) / len(gaps), 2)


def size_variation_flag(history: List[Dict[str, Any]]) -> int:
    """
    Classic wardrobing signal: buying the same product in 3+ different sizes.
    Returns 1 if flagged (fraud signal), 0 otherwise.
    Wardrobers order multiple sizes, pick the best-fitting one, return the rest.
    """
    product_sizes: Dict[str, set] = defaultdict(set)
    for t in history:
        if t["action_type"] == "Purchase" and t.get("product_id") and t.get("size_variant"):
            product_sizes[t["product_id"]].add(t["size_variant"])
    # Flag if any single product was ordered in 3+ distinct sizes
    return int(any(len(sizes) >= 3 for sizes in product_sizes.values()))


def category_diversity_score(history: List[Dict[str, Any]]) -> float:
    """
    Fraudsters in return schemes often concentrate on high-value categories
    (Clothing, Electronics). Normal shoppers have diverse category spread.
    Returns ratio of unique purchase categories to total purchases.
    """
    purchases = [t for t in history if t["action_type"] == "Purchase"]
    if not purchases:
        return 0.0
    categories = {t.get("product_category") for t in purchases if t.get("product_category")}
    return round(len(categories) / len(purchases), 4)


def avg_order_value(history: List[Dict[str, Any]]) -> float:
    """Average value of purchase orders."""
    purchases = [t for t in history if t["action_type"] == "Purchase" and t.get("order_value")]
    if not purchases:
        return 0.0
    return round(sum(float(t["order_value"]) for t in purchases) / len(purchases), 2)


def total_purchases(history: List[Dict[str, Any]]) -> int:
    return sum(1 for t in history if t["action_type"] == "Purchase")


def total_returns(history: List[Dict[str, Any]]) -> int:
    return sum(1 for t in history if t["action_type"] == "ReturnRequest")


def assemble_features(history: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Assembles the full feature vector for ML model inference.
    Feature names MUST match those used during model training.
    """
    return {
        "return_to_purchase_ratio": return_to_purchase_ratio(history),
        "temporal_gap_days": temporal_gap_score(history),
        "size_variation_flag": float(size_variation_flag(history)),
        "category_diversity": category_diversity_score(history),
        "avg_order_value": avg_order_value(history),
        "total_purchases": float(total_purchases(history)),
        "total_returns": float(total_returns(history)),
    }


def get_reason_codes(features: Dict[str, float]) -> List[str]:
    """Generate human-readable reason codes for transparency / explainability."""
    reasons = []
    if features["return_to_purchase_ratio"] > 0.5:
        reasons.append("high_return_ratio")
    if features["temporal_gap_days"] < 3 and features["total_returns"] > 0:
        reasons.append("rapid_return_pattern")
    if features["size_variation_flag"] == 1.0:
        reasons.append("size_variation_detected")
    if features["avg_order_value"] > 5000 and features["return_to_purchase_ratio"] > 0.3:
        reasons.append("high_value_return_risk")
    if features["total_returns"] >= 5:
        reasons.append("excessive_return_count")
    return reasons if reasons else ["no_significant_flags"]
