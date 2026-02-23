"""
Synthetic Transaction Data Generator
=====================================
Generates 10,000 realistic e-commerce transaction records.
Distribution: ~98% legitimate users, ~2% fraud seeds.
Output: data/synthetic_transactions.csv
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib
import os

np.random.seed(42)
random.seed(42)

N_USERS = 500
N_LEGITIMATE = 490
CATEGORIES = ["Clothing", "Electronics", "Footwear", "Accessories", "Books", "Sports"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
records = []

def fake_user_hash(idx: int) -> str:
    return hashlib.sha256(f"user_{idx}@example.com:hackathon-salt".encode()).hexdigest()

def random_date(start_days_ago: int, end_days_ago: int) -> datetime:
    delta = random.randint(end_days_ago, start_days_ago)
    return datetime.now() - timedelta(days=delta)


# ── LEGITIMATE USERS (low return ratio, slow returns, no wardrobing)
print("Generating legitimate user transactions...")
for i in range(N_LEGITIMATE):
    user_hash = fake_user_hash(i)
    n_purchases = random.randint(2, 20)
    n_returns = random.randint(0, max(1, int(n_purchases * 0.15)))  # ≤15% return rate

    cat = random.choice(CATEGORIES)
    for j in range(n_purchases):
        purchase_date = random_date(365, 7)
        delivery_date = purchase_date + timedelta(days=random.randint(2, 5))
        order_id = f"ORD_L{i}_{j}"
        records.append({
            "user_hash": user_hash,
            "action_type": "Purchase",
            "timestamp": purchase_date,
            "order_value": round(random.uniform(199, 8000), 2),
            "product_category": random.choice(CATEGORIES),
            "product_id": f"PROD_{random.randint(100, 999)}",
            "size_variant": random.choice(SIZES) if cat == "Clothing" else None,
            "delivery_date": delivery_date,
            "return_date": None,
            "order_id": order_id,
            "is_fraud": 0,
        })

    # Some returns — with a realistic gap (7–21 days)
    chosen_orders = random.sample(range(n_purchases), min(n_returns, n_purchases))
    for j in chosen_orders:
        base = records[-(n_purchases - j)]
        return_date = base["delivery_date"] + timedelta(days=random.randint(7, 21))
        records.append({
            **base,
            "action_type": "ReturnRequest",
            "return_date": return_date,
            "timestamp": return_date,
        })


# ── FRAUD USERS (high return ratio, rapid returns, wardrobing)
print("Generating fraud user transactions...")
for i in range(N_LEGITIMATE, N_USERS):
    user_hash = fake_user_hash(i)
    fraud_type = random.choice(["wardrober", "rapid_returner", "serial_fraud"])
    n_purchases = random.randint(5, 30)
    cat = "Clothing" if fraud_type == "wardrober" else random.choice(CATEGORIES)

    product_id = f"PROD_FRAUD_{i}"
    sizes_used = random.sample(SIZES, min(random.randint(3, 5), len(SIZES)))

    for j in range(n_purchases):
        purchase_date = random_date(365, 7)
        delivery_date = purchase_date + timedelta(days=random.randint(2, 4))
        order_id = f"ORD_F{i}_{j}"
        size = sizes_used[j % len(sizes_used)] if fraud_type == "wardrober" else random.choice(SIZES)
        records.append({
            "user_hash": user_hash,
            "action_type": "Purchase",
            "timestamp": purchase_date,
            "order_value": round(random.uniform(1500, 12000), 2),
            "product_category": cat,
            "product_id": product_id if fraud_type == "wardrober" else f"PROD_{random.randint(100,999)}",
            "size_variant": size,
            "delivery_date": delivery_date,
            "return_date": None,
            "order_id": order_id,
            "is_fraud": 1,
        })

        # High return rate for fraud users (60–95%)
        if random.random() < 0.80:
            gap = random.randint(1, 3) if fraud_type in ("rapid_returner", "wardrober") else random.randint(1, 7)
            return_date = delivery_date + timedelta(days=gap)
            records.append({
                "user_hash": user_hash,
                "action_type": "ReturnRequest",
                "timestamp": return_date,
                "order_value": records[-1]["order_value"],
                "product_category": cat,
                "product_id": records[-1]["product_id"],
                "size_variant": size,
                "delivery_date": delivery_date,
                "return_date": return_date,
                "order_id": order_id,
                "is_fraud": 1,
            })


df = pd.DataFrame(records)
os.makedirs("data", exist_ok=True)
df.to_csv("data/synthetic_transactions.csv", index=False)
print(f"✅ Generated {len(df)} transaction records for {N_USERS} users")
print(f"   Legitimate users: {N_LEGITIMATE} | Fraud users: {N_USERS - N_LEGITIMATE}")
print(f"   Saved to data/synthetic_transactions.csv")
