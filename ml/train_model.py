"""
Model Training Pipeline
========================
1. Loads engineered features from data/features.csv
2. Applies SMOTE to balance the fraud/legit class imbalance
3. Trains XGBoost classifier
4. Evaluates and prints metrics
5. Saves models/fraud_model.pkl + models/feature_names.json
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, f1_score
)
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb

print("=" * 60)
print("  ReturnGuard AI — XGBoost + SMOTE Training Pipeline")
print("=" * 60)

# ── 1. Load Features
print("\n[1/5] Loading feature matrix...")
df = pd.read_csv("data/features.csv")
print(f"    Shape: {df.shape}")
print(f"    Class distribution → Legit: {(df['is_fraud']==0).sum()}, Fraud: {df['is_fraud'].sum()}")

FEATURE_COLS = [
    "return_to_purchase_ratio",
    "temporal_gap_days",
    "size_variation_flag",
    "category_diversity",
    "avg_order_value",
    "total_purchases",
    "total_returns",
]

X = df[FEATURE_COLS].values
y = df["is_fraud"].values

# ── 2. Train/Test Split (stratified to preserve imbalance)
print("\n[2/5] Splitting data (80/20 stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"    Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# ── 3. SMOTE — Synthetic Minority Over-sampling
print("\n[3/5] Applying SMOTE to balance training classes...")
smote = SMOTE(random_state=42, k_neighbors=min(5, y_train.sum() - 1))
X_res, y_res = smote.fit_resample(X_train, y_train)
print(f"    Before SMOTE → Legit: {(y_train==0).sum()}, Fraud: {y_train.sum()}")
print(f"    After  SMOTE → Legit: {(y_res==0).sum()}, Fraud: {y_res.sum()}")

# ── 4. Train XGBoost
print("\n[4/5] Training XGBoost classifier...")
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=1,   # SMOTE already balanced classes
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
    verbosity=0,
)
model.fit(X_res, y_res)

# ── 5. Evaluate
print("\n[5/5] Evaluating on held-out test set...")
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"    TN={cm[0,0]}  FP={cm[0,1]}")
print(f"    FN={cm[1,0]}  TP={cm[1,1]}")

roc_auc = roc_auc_score(y_test, y_proba)
f1 = f1_score(y_test, y_pred)
print(f"\n    ROC-AUC : {roc_auc:.4f}")
print(f"    F1 Score: {f1:.4f}")

# Feature Importances
print("\nFeature Importances:")
importances = model.feature_importances_
for feat, imp in sorted(zip(FEATURE_COLS, importances), key=lambda x: -x[1]):
    bar = "█" * int(imp * 40)
    print(f"  {feat:<35} {bar} ({imp:.4f})")

# ── Save Model
os.makedirs("models", exist_ok=True)
model_path = "models/fraud_model.pkl"
feature_names_path = "models/feature_names.json"

joblib.dump(model, model_path)
with open(feature_names_path, "w") as f:
    json.dump(FEATURE_COLS, f)

print(f"\n✅ Model saved to {model_path}")
print(f"✅ Feature names saved to {feature_names_path}")
print(f"\n{'='*60}")
print(f"  Training complete! ROC-AUC: {roc_auc:.4f}, F1: {f1:.4f}")
print(f"{'='*60}")
