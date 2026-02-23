from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import json

from db import get_db
from models.orm_models import User, Transaction, RiskScore
from features.engineer import assemble_features, get_reason_codes
from services import model_service

router = APIRouter(prefix="/v1", tags=["Risk Scoring"])


class CartItem(BaseModel):
    product_id: str
    category: str
    size: Optional[str] = None
    value: float


class RiskScoreRequest(BaseModel):
    user_hash: str
    cart: List[CartItem] = []


class RiskScoreResponse(BaseModel):
    user_hash: str
    risk_score: int              # 0–100
    risk_level: str              # LOW | MEDIUM | HIGH
    reason_codes: List[str]
    features_used: dict
    model_used: str


def _classify_level(score: int) -> str:
    if score > 80:
        return "HIGH"
    elif score > 50:
        return "MEDIUM"
    return "LOW"


@router.post("/get-risk-score", response_model=RiskScoreResponse,
             summary="Get real-time fraud risk score for a user")
async def get_risk_score(payload: RiskScoreRequest, db: AsyncSession = Depends(get_db)):
    """
    Core inference endpoint.
    1. Fetches user's transaction history from DB
    2. Engineers behavioral features
    3. Runs XGBoost model (or heuristic fallback)
    4. Returns 0–100 risk score + explainable reason codes
    """
    # Fetch transaction history
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_hash == payload.user_hash)
        .order_by(Transaction.timestamp.desc())
        .limit(200)
    )
    transactions = result.scalars().all()

    history = [
        {
            "action_type": t.action_type,
            "product_id": t.product_id,
            "product_category": t.product_category,
            "order_value": float(t.order_value) if t.order_value else None,
            "size_variant": t.size_variant,
            "delivery_date": t.delivery_date,
            "return_date": t.return_date,
        }
        for t in transactions
    ]

    # Engineer features
    features = assemble_features(history)
    reason_codes = get_reason_codes(features)

    # Model inference
    proba = model_service.predict(features)
    score = model_service.score_to_100(proba)
    level = _classify_level(score)

    # Persist score
    user_result = await db.execute(select(User).where(User.user_hash == payload.user_hash))
    user = user_result.scalar_one_or_none()
    if user:
        user.risk_tier = level
        risk_entry = RiskScore(
            user_hash=payload.user_hash,
            risk_score=score,
            risk_level=level,
            reason_codes=json.dumps(reason_codes),
            model_version="v1.0",
        )
        db.add(risk_entry)

    model_used = "XGBoost" if model_service._model is not None else "heuristic_fallback"

    return RiskScoreResponse(
        user_hash=payload.user_hash,
        risk_score=score,
        risk_level=level,
        reason_codes=reason_codes,
        features_used=features,
        model_used=model_used,
    )


@router.get("/score-history/{user_hash}", summary="Get historical risk scores for a user")
async def score_history(user_hash: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.user_hash == user_hash)
        .order_by(RiskScore.computed_at.desc())
        .limit(20)
    )
    scores = result.scalars().all()
    return {
        "user_hash": user_hash,
        "scores": [
            {
                "risk_score": float(s.risk_score),
                "risk_level": s.risk_level,
                "reason_codes": json.loads(s.reason_codes) if s.reason_codes else [],
                "computed_at": s.computed_at.isoformat() if s.computed_at else None,
            }
            for s in scores
        ],
    }
