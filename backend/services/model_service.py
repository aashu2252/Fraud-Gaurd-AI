"""
Model Service — Loads and runs the fraud detection model (RandomForest / XGBoost).

Falls back to a rule-based heuristic score if the model file
hasn't been trained yet (allows frontend demo without running ML pipeline first).
"""
import os
import json
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

_model = None
_feature_names: List[str] = []
_model_type: str = "none"

EXPECTED_FEATURES = [
    "return_to_purchase_ratio",
    "temporal_gap_days",
    "size_variation_flag",
    "category_diversity",
    "avg_order_value",
    "total_purchases",
    "total_returns",
]


def load_model(model_path: str, feature_names_path: str):
    """Load the trained model at application startup."""
    global _model, _feature_names
    try:
        import joblib
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
            logger.info(f"✅ ML model loaded from {model_path}")
        else:
            logger.warning(f"⚠️  Model not found at {model_path}. Using rule-based fallback.")

        if os.path.exists(feature_names_path):
            with open(feature_names_path) as f:
                _feature_names = json.load(f)
        else:
            _feature_names = EXPECTED_FEATURES
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model = None
        _feature_names = EXPECTED_FEATURES


def predict(features: Dict[str, float]) -> float:
    """
    Returns a fraud probability in [0, 1].
    If model is loaded -> uses XGBoost.
    Fallback -> rule-based heuristic for demo purposes.
    """
    if _model is not None:
        try:
            feature_vector = np.array([[features.get(f, 0.0) for f in _feature_names]])
            proba = _model.predict_proba(feature_vector)[0][1]
            return float(proba)
        except Exception as e:
            logger.error(f"Model inference failed: {e}. Falling back to heuristic.")

    # --- Rule-based fallback heuristic ---
    score = 0.0
    rpr = features.get("return_to_purchase_ratio", 0)
    gap = features.get("temporal_gap_days", 30)
    size_flag = features.get("size_variation_flag", 0)
    returns = features.get("total_returns", 0)

    score += min(rpr * 0.5, 0.5)          # up to 50% weight
    if gap < 3 and returns > 0:
        score += 0.20                       # rapid return
    if size_flag == 1:
        score += 0.20                       # wardrobing
    if returns >= 5:
        score += 0.10                       # excessive returns

    return min(score, 1.0)


def score_to_100(proba: float) -> int:
    """Convert [0,1] probability to integer 0–100 risk score."""
    return int(round(proba * 100))
