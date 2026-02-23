"""
Model Evaluation Script
========================
Loads the saved model and generates a detailed evaluation report.
Run this after train_model.py to verify model quality.
"""
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, RocCurveDisplay
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

print("Loading model and data...")
model = joblib.load("models/fraud_model.pkl")
with open("models/feature_names.json") as f:
    feature_cols = json.load(f)

df = pd.read_csv("data/features.csv")
X = df[feature_cols].values
y = df["is_fraud"].values

y_pred = model.predict(X)
y_proba = model.predict_proba(X)[:, 1]

print("\n" + "="*60)
print("  FULL DATASET EVALUATION REPORT")
print("="*60)
print(classification_report(y, y_pred, target_names=["Legit", "Fraud"]))
print(f"ROC-AUC: {roc_auc_score(y, y_proba):.4f}")

cm = confusion_matrix(y, y_pred)
print(f"\nConfusion Matrix:\n  TN={cm[0,0]}  FP={cm[0,1]}\n  FN={cm[1,0]}  TP={cm[1,1]}")

print("\nTop Feature Importances:")
imps = list(zip(feature_cols, model.feature_importances_))
for feat, imp in sorted(imps, key=lambda x: -x[1]):
    print(f"  {feat:<35} {imp:.4f}")

# Plot feature importance
fig, ax = plt.subplots(figsize=(8, 5))
names, vals = zip(*sorted(imps, key=lambda x: x[1]))
ax.barh(names, vals, color="#7C3AED")
ax.set_xlabel("Feature Importance (XGBoost)")
ax.set_title("ReturnGuard AI — Feature Importance")
plt.tight_layout()
plt.savefig("models/feature_importance.png", dpi=150)
print("\n✅ Feature importance chart saved to models/feature_importance.png")
