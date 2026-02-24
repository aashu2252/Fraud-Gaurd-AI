"""
startup_train.py — Render startup script

Runs the ML training pipeline if fraud_model.pkl is missing,
then starts the FastAPI app via uvicorn.

Usage (as Render start command):
    python startup_train.py
"""
import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("startup_train")

# ── Paths ─────────────────────────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
ML_DIR      = BACKEND_DIR.parent / "ml"
MODELS_DIR  = ML_DIR / "models"
MODEL_PKL   = MODELS_DIR / "fraud_model.pkl"
FEAT_JSON   = MODELS_DIR / "feature_names.json"

FEATURE_COLS = [
    "return_to_purchase_ratio",
    "temporal_gap_days",
    "size_variation_flag",
    "category_diversity",
    "avg_order_value",
    "total_purchases",
    "total_returns",
]


def train_model():
    """Inline ML pipeline: generate data → engineer features → train model."""
    import numpy as np
    import pandas as pd
    import random
    import hashlib
    import joblib
    from datetime import datetime, timedelta
    from collections import defaultdict
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.utils import resample

    np.random.seed(42)
    random.seed(42)

    data_dir = ML_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Generate synthetic transactions ───────────────────────────────
    log.info("[1/3] Generating synthetic transactions...")
    N_USERS, N_LEGIT = 500, 480
    CATS  = ["Clothing","Electronics","Footwear","Accessories","Books","Sports"]
    SIZES = ["XS","S","M","L","XL","XXL"]
    records = []

    def fhash(i):
        return hashlib.sha256(f"user_{i}@example.com:hackathon-salt".encode()).hexdigest()

    def rdate(start, end):
        return datetime.now() - timedelta(days=random.randint(end, start))

    for i in range(N_LEGIT):
        uh = fhash(i); cat = random.choice(CATS); n_p = random.randint(2, 20)
        n_r = random.randint(0, max(1, int(n_p * 0.15)))
        for j in range(n_p):
            pd_ = rdate(365, 7); dd = pd_ + timedelta(days=random.randint(2, 5))
            records.append({"user_hash": uh, "action_type": "Purchase", "timestamp": pd_,
                "order_value": round(random.uniform(199, 8000), 2), "product_category": random.choice(CATS),
                "product_id": f"PROD_{random.randint(100,999)}",
                "size_variant": random.choice(SIZES) if cat == "Clothing" else None,
                "delivery_date": dd, "return_date": None, "order_id": f"L{i}_{j}", "is_fraud": 0})
        for j in range(min(n_r, n_p)):
            base = records[-(n_p - j)]
            ret = base["delivery_date"] + timedelta(days=random.randint(7, 21))
            records.append({**base, "action_type": "ReturnRequest", "return_date": ret, "timestamp": ret})

    for i in range(N_LEGIT, N_USERS):
        uh = fhash(i); ft = random.choice(["wardrober","rapid_returner","serial_fraud"])
        cat = "Clothing" if ft == "wardrober" else random.choice(CATS)
        n_p = random.randint(5, 30); pid = f"PROD_FRAUD_{i}"
        sizes_used = random.sample(SIZES, min(random.randint(3, 5), 6))
        for j in range(n_p):
            pd_ = rdate(365, 7); dd = pd_ + timedelta(days=random.randint(2, 4))
            sz = sizes_used[j % len(sizes_used)] if ft == "wardrober" else random.choice(SIZES)
            records.append({"user_hash": uh, "action_type": "Purchase", "timestamp": pd_,
                "order_value": round(random.uniform(1500, 12000), 2), "product_category": cat,
                "product_id": pid if ft == "wardrober" else f"PROD_{random.randint(100,999)}",
                "size_variant": sz, "delivery_date": dd, "return_date": None,
                "order_id": f"F{i}_{j}", "is_fraud": 1})
            if random.random() < 0.80:
                gap = random.randint(1, 3) if ft in ("rapid_returner","wardrober") else random.randint(1, 7)
                ret = dd + timedelta(days=gap)
                records.append({**records[-1], "action_type": "ReturnRequest", "timestamp": ret, "return_date": ret})

    df = pd.DataFrame(records)
    df.to_csv(data_dir / "synthetic_transactions.csv", index=False)
    log.info(f"   ✅ {len(df)} transaction rows, {N_USERS} users")

    # ── Step 2: Feature engineering ───────────────────────────────────────────
    log.info("[2/3] Engineering features...")
    df = pd.read_csv(data_dir / "synthetic_transactions.csv",
                     parse_dates=["timestamp","delivery_date","return_date"])
    rows = []
    for uh in df["user_hash"].unique():
        utx = df[df["user_hash"] == uh]
        purchases = utx[utx["action_type"] == "Purchase"]
        returns   = utx[utx["action_type"] == "ReturnRequest"]
        n_p, n_r = len(purchases), len(returns)
        rpr = n_r / n_p if n_p else 0.0
        rwd = returns.dropna(subset=["delivery_date","return_date"])
        gaps = [(r["return_date"] - r["delivery_date"]).days for _, r in rwd.iterrows()]
        avg_gap = float(np.mean(gaps)) if gaps else 30.0
        pws = purchases.dropna(subset=["product_id","size_variant"])
        ps = defaultdict(set)
        for _, r in pws.iterrows():
            ps[r["product_id"]].add(r["size_variant"])
        sz_flag = int(any(len(v) >= 3 for v in ps.values()))
        cats = purchases["product_category"].dropna().nunique()
        cat_div = round(cats / n_p, 4) if n_p else 0.0
        avg_val = float(purchases["order_value"].mean()) if n_p else 0.0
        is_fraud = int(utx["is_fraud"].mode()[0]) if "is_fraud" in utx else 0
        rows.append({"user_hash": uh, "return_to_purchase_ratio": round(rpr, 4),
            "temporal_gap_days": round(avg_gap, 2), "size_variation_flag": float(sz_flag),
            "category_diversity": cat_div, "avg_order_value": round(avg_val, 2),
            "total_purchases": float(n_p), "total_returns": float(n_r), "is_fraud": is_fraud})
    fdf = pd.DataFrame(rows)
    fdf.to_csv(data_dir / "features.csv", index=False)
    log.info(f"   ✅ {fdf.shape[0]} users, {fdf['is_fraud'].sum()} fraud, {(fdf['is_fraud']==0).sum()} legit")

    # ── Step 3: Train RandomForest ────────────────────────────────────────────
    log.info("[3/3] Training RandomForest classifier...")
    X = fdf[FEATURE_COLS].values
    y = fdf["is_fraud"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    fraud_idx = np.where(y_train == 1)[0]
    legit_idx = np.where(y_train == 0)[0]
    fraud_up_X = resample(X_train[fraud_idx], n_samples=len(legit_idx), random_state=42)
    fraud_up_y = np.ones(len(legit_idx), dtype=int)
    X_bal = np.vstack([X_train[legit_idx], fraud_up_X])
    y_bal = np.concatenate([y_train[legit_idx], fraud_up_y])

    model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_leaf=2,
                                   class_weight="balanced", random_state=42, n_jobs=-1)
    model.fit(X_bal, y_bal)

    joblib.dump(model, MODEL_PKL)
    with open(FEAT_JSON, "w") as f:
        json.dump(FEATURE_COLS, f)

    log.info(f"   ✅ Model saved → {MODEL_PKL}")
    log.info(f"   ✅ Feature names saved → {FEAT_JSON}")


# ── Main entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not MODEL_PKL.exists() or not FEAT_JSON.exists():
        log.info("🔧 ML model not found — running training pipeline...")
        try:
            train_model()
            log.info("✅ Training complete!")
        except Exception as e:
            log.error(f"❌ Training failed: {e}")
            log.warning("⚠️  Falling back to rule-based scoring (app will still start)")
    else:
        log.info(f"✅ Model already exists at {MODEL_PKL} — skipping training.")

    # Start the FastAPI app
    log.info("🚀 Starting uvicorn...")
    os.chdir(BACKEND_DIR)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), log_level="info")
