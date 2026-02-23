"""
Feature Engineering Script
============================
Transforms raw transaction records → per-user feature vectors.
Matches the features produced by backend/features/engineer.py
Output: data/features.csv
"""
import pandas as pd
import numpy as np
from collections import defaultdict
import os

print("Loading synthetic transactions...")
df = pd.read_csv("data/synthetic_transactions.csv", parse_dates=["timestamp", "delivery_date", "return_date"])

print(f"Loaded {len(df)} rows, {df['user_hash'].nunique()} unique users")

users = df["user_hash"].unique()
feature_rows = []

for user_hash in users:
    utx = df[df["user_hash"] == user_hash]
    purchases = utx[utx["action_type"] == "Purchase"]
    returns = utx[utx["action_type"] == "ReturnRequest"]

    # 1. Return-to-Purchase Ratio
    n_purchases = len(purchases)
    n_returns = len(returns)
    rpr = n_returns / n_purchases if n_purchases > 0 else 0.0

    # 2. Temporal Gap (avg days between delivery and return)
    gaps = []
    ret_with_dates = returns.dropna(subset=["delivery_date", "return_date"])
    for _, row in ret_with_dates.iterrows():
        gap = max(0, (row["return_date"] - row["delivery_date"]).days)
        gaps.append(gap)
    avg_gap = np.mean(gaps) if gaps else 30.0

    # 3. Size Variation Flag (same product, 3+ sizes → wardrobing)
    purch_with_size = purchases.dropna(subset=["product_id", "size_variant"])
    product_sizes = defaultdict(set)
    for _, row in purch_with_size.iterrows():
        product_sizes[row["product_id"]].add(row["size_variant"])
    size_flag = int(any(len(s) >= 3 for s in product_sizes.values()))

    # 4. Category Diversity
    cats = purchases["product_category"].dropna().nunique()
    cat_diversity = round(cats / n_purchases, 4) if n_purchases > 0 else 0.0

    # 5. Avg Order Value
    avg_value = float(purchases["order_value"].mean()) if n_purchases > 0 else 0.0

    # Label — majority vote from transaction labels
    is_fraud = int(utx["is_fraud"].mode()[0]) if "is_fraud" in utx.columns else 0

    feature_rows.append({
        "user_hash": user_hash,
        "return_to_purchase_ratio": round(rpr, 4),
        "temporal_gap_days": round(avg_gap, 2),
        "size_variation_flag": float(size_flag),
        "category_diversity": cat_diversity,
        "avg_order_value": round(avg_value, 2),
        "total_purchases": float(n_purchases),
        "total_returns": float(n_returns),
        "is_fraud": is_fraud,
    })

features_df = pd.DataFrame(feature_rows)
features_df.to_csv("data/features.csv", index=False)

print(f"\n✅ Feature matrix saved: {features_df.shape[0]} users × {features_df.shape[1]-2} features")
print(f"   Fraud users: {features_df['is_fraud'].sum()} | Legit users: {(features_df['is_fraud']==0).sum()}")
print(f"   Class imbalance ratio: {(features_df['is_fraud']==0).sum()}/{features_df['is_fraud'].sum()}")
print("\nFeature statistics:")
print(features_df.drop(columns=["user_hash", "is_fraud"]).describe().round(3))
