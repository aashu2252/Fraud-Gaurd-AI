"""
Updated run_all.py — uses RandomForestClassifier (scikit-learn only, works on Python 3.14)
Includes manual SMOTE-equivalent via random oversampling of the minority class.
"""
import sys, os, logging, json

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_run.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
log.info(f"Working dir: {os.getcwd()}")
log.info(f"Python: {sys.version}")

# ── STEP 1: Generate synthetic data ──────────────────────────────────
log.info("="*50)
log.info("STEP 1: Generating synthetic transactions...")
try:
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    import random, hashlib

    np.random.seed(42); random.seed(42)
    N_USERS, N_LEGIT = 500, 480
    CATS = ["Clothing","Electronics","Footwear","Accessories","Books","Sports"]
    SIZES = ["XS","S","M","L","XL","XXL"]
    records = []

    def fhash(i):
        return hashlib.sha256(f"user_{i}@example.com:hackathon-salt".encode()).hexdigest()

    def rdate(start, end):
        return datetime.now() - timedelta(days=random.randint(end, start))

    for i in range(N_LEGIT):
        uh = fhash(i); cat = random.choice(CATS); n_p = random.randint(2,20)
        n_r = random.randint(0, max(1, int(n_p*0.15)))
        for j in range(n_p):
            pd_  = rdate(365, 7); dd = pd_ + timedelta(days=random.randint(2,5))
            records.append({"user_hash":uh,"action_type":"Purchase","timestamp":pd_,
                "order_value":round(random.uniform(199,8000),2),"product_category":random.choice(CATS),
                "product_id":f"PROD_{random.randint(100,999)}",
                "size_variant":random.choice(SIZES) if cat=="Clothing" else None,
                "delivery_date":dd,"return_date":None,"order_id":f"L{i}_{j}","is_fraud":0})
        for j in range(min(n_r, n_p)):
            base = records[-(n_p-j)]; ret = base["delivery_date"] + timedelta(days=random.randint(7,21))
            records.append({**base,"action_type":"ReturnRequest","return_date":ret,"timestamp":ret})

    for i in range(N_LEGIT, N_USERS):
        uh = fhash(i); ft = random.choice(["wardrober","rapid_returner","serial_fraud"])
        cat = "Clothing" if ft=="wardrober" else random.choice(CATS)
        n_p = random.randint(5,30); pid = f"PROD_FRAUD_{i}"
        sizes_used = random.sample(SIZES, min(random.randint(3,5),6))
        for j in range(n_p):
            pd_ = rdate(365,7); dd = pd_ + timedelta(days=random.randint(2,4))
            sz = sizes_used[j%len(sizes_used)] if ft=="wardrober" else random.choice(SIZES)
            records.append({"user_hash":uh,"action_type":"Purchase","timestamp":pd_,
                "order_value":round(random.uniform(1500,12000),2),"product_category":cat,
                "product_id":pid if ft=="wardrober" else f"PROD_{random.randint(100,999)}",
                "size_variant":sz,"delivery_date":dd,"return_date":None,
                "order_id":f"F{i}_{j}","is_fraud":1})
            if random.random() < 0.80:
                gap = random.randint(1,3) if ft in ("rapid_returner","wardrober") else random.randint(1,7)
                ret = dd + timedelta(days=gap)
                records.append({**records[-1],"action_type":"ReturnRequest","timestamp":ret,"return_date":ret})

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(records); df.to_csv("data/synthetic_transactions.csv", index=False)
    log.info(f"✅ Generated {len(df)} rows, {N_USERS} users ({N_LEGIT} legit, {N_USERS-N_LEGIT} fraud)")
except Exception:
    import traceback; log.error("FAILED Step1:\n"+traceback.format_exc()); sys.exit(1)

# ── STEP 2: Feature Engineering ───────────────────────────────────────
log.info("="*50)
log.info("STEP 2: Engineering features...")
try:
    from collections import defaultdict
    df = pd.read_csv("data/synthetic_transactions.csv", parse_dates=["timestamp","delivery_date","return_date"])
    rows = []
    for uh in df["user_hash"].unique():
        utx = df[df["user_hash"]==uh]
        purchases = utx[utx["action_type"]=="Purchase"]
        returns   = utx[utx["action_type"]=="ReturnRequest"]
        n_p, n_r = len(purchases), len(returns)
        rpr = n_r/n_p if n_p else 0.0
        rwd = returns.dropna(subset=["delivery_date","return_date"])
        gaps = [(r["return_date"]-r["delivery_date"]).days for _,r in rwd.iterrows()]
        avg_gap = float(np.mean(gaps)) if gaps else 30.0
        pws = purchases.dropna(subset=["product_id","size_variant"])
        ps = defaultdict(set)
        for _,r in pws.iterrows(): ps[r["product_id"]].add(r["size_variant"])
        sz_flag = int(any(len(v)>=3 for v in ps.values()))
        cats = purchases["product_category"].dropna().nunique()
        cat_div = round(cats/n_p,4) if n_p else 0.0
        avg_val = float(purchases["order_value"].mean()) if n_p else 0.0
        is_fraud = int(utx["is_fraud"].mode()[0]) if "is_fraud" in utx else 0
        rows.append({"user_hash":uh,"return_to_purchase_ratio":round(rpr,4),
            "temporal_gap_days":round(avg_gap,2),"size_variation_flag":float(sz_flag),
            "category_diversity":cat_div,"avg_order_value":round(avg_val,2),
            "total_purchases":float(n_p),"total_returns":float(n_r),"is_fraud":is_fraud})
    fdf = pd.DataFrame(rows); fdf.to_csv("data/features.csv", index=False)
    log.info(f"✅ Features: {fdf.shape} | Fraud: {fdf['is_fraud'].sum()} | Legit: {(fdf['is_fraud']==0).sum()}")
except Exception:
    import traceback; log.error("FAILED Step2:\n"+traceback.format_exc()); sys.exit(1)

# ── STEP 3: Train RandomForest (sklearn, Python 3.14 compatible) ───────
log.info("="*50)
log.info("STEP 3: Training RandomForest classifier (sklearn - Python 3.14 compatible)...")
try:
    import joblib
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score, f1_score, confusion_matrix
    from sklearn.utils import resample

    FEATURE_COLS = ["return_to_purchase_ratio","temporal_gap_days","size_variation_flag",
                    "category_diversity","avg_order_value","total_purchases","total_returns"]
    fdf = pd.read_csv("data/features.csv")
    X = fdf[FEATURE_COLS].values; y = fdf["is_fraud"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    log.info(f"   Train: {len(X_train)} | Test: {len(X_test)}")

    # Manual oversampling (replaces SMOTE for Python 3.14 compatibility)
    fraud_idx = np.where(y_train == 1)[0]
    legit_idx = np.where(y_train == 0)[0]
    log.info(f"   Before balance → Legit: {len(legit_idx)} | Fraud: {len(fraud_idx)}")
    fraud_upsampled_X = resample(X_train[fraud_idx], n_samples=len(legit_idx), random_state=42)
    fraud_upsampled_y = np.ones(len(legit_idx), dtype=int)
    X_bal = np.vstack([X_train[legit_idx], fraud_upsampled_X])
    y_bal = np.concatenate([y_train[legit_idx], fraud_upsampled_y])
    log.info(f"   After balance → Legit: {(y_bal==0).sum()} | Fraud: {(y_bal==1).sum()}")

    model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_leaf=2,
                                    class_weight="balanced", random_state=42, n_jobs=-1)
    model.fit(X_bal, y_bal)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    roc = roc_auc_score(y_test, y_proba)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    log.info(f"   ROC-AUC: {roc:.4f} | F1: {f1:.4f}")
    log.info(f"   Confusion Matrix: TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
    log.info("Classification Report:\n" + classification_report(y_test, y_pred,
             target_names=["Legit","Fraud"], zero_division=0))

    imps = sorted(zip(FEATURE_COLS, model.feature_importances_), key=lambda x: -x[1])
    log.info("Feature Importances:")
    for feat, imp in imps:
        bar = "█" * int(imp * 40)
        log.info(f"  {feat:<35} {bar} ({imp:.4f})")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/fraud_model.pkl")
    with open("models/feature_names.json", "w") as f: json.dump(FEATURE_COLS, f)
    # Save metadata
    with open("models/model_meta.json", "w") as f:
        json.dump({"model_type":"RandomForestClassifier","roc_auc":round(roc,4),
                   "f1_score":round(f1,4),"n_estimators":200,"python_version":sys.version}, f, indent=2)
    log.info("✅ Model saved → models/fraud_model.pkl")
except Exception:
    import traceback; log.error("FAILED Step3:\n"+traceback.format_exc()); sys.exit(1)

log.info("="*50)
log.info("🎉 ML PIPELINE COMPLETE — RandomForest model ready!")
