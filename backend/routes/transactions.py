from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from db import get_db
from models.orm_models import User, Transaction

router = APIRouter(prefix="/v1", tags=["Transactions"])


class LogActionRequest(BaseModel):
    user_hash: str
    action_type: str            # View | AddToCart | Purchase | ReturnRequest
    product_id: Optional[str] = None
    product_category: Optional[str] = None
    order_value: Optional[float] = None
    size_variant: Optional[str] = None
    delivery_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    order_id: Optional[str] = None
    store_id: Optional[str] = None


VALID_ACTION_TYPES = {"View", "AddToCart", "Purchase", "ReturnRequest"}


@router.post("/log-action", summary="Log a user behavioral action")
async def log_action(payload: LogActionRequest, db: AsyncSession = Depends(get_db)):
    """
    Records a behavioral fingerprint event (View, AddToCart, Purchase, or ReturnRequest).
    Upserts the user record if it doesn't exist yet.
    """
    if payload.action_type not in VALID_ACTION_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"action_type must be one of {sorted(VALID_ACTION_TYPES)}"
        )

    # Upsert user
    result = await db.execute(select(User).where(User.user_hash == payload.user_hash))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            user_hash=payload.user_hash,
            store_id=payload.store_id,
            first_seen_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()

    # Insert transaction
    txn = Transaction(
        user_hash=payload.user_hash,
        action_type=payload.action_type,
        timestamp=datetime.now(timezone.utc),
        order_value=payload.order_value,
        product_category=payload.product_category,
        product_id=payload.product_id,
        size_variant=payload.size_variant,
        delivery_date=payload.delivery_date,
        return_date=payload.return_date,
        order_id=payload.order_id,
    )
    db.add(txn)

    return {
        "status": "recorded",
        "user_hash": payload.user_hash,
        "action_type": payload.action_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/history/{user_hash}", summary="Get transaction history for a user")
async def get_history(user_hash: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_hash == user_hash)
        .order_by(Transaction.timestamp.desc())
        .limit(100)
    )
    transactions = result.scalars().all()
    return {
        "user_hash": user_hash,
        "count": len(transactions),
        "transactions": [
            {
                "action_type": t.action_type,
                "product_id": t.product_id,
                "product_category": t.product_category,
                "order_value": float(t.order_value) if t.order_value else None,
                "size_variant": t.size_variant,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "delivery_date": t.delivery_date.isoformat() if t.delivery_date else None,
                "return_date": t.return_date.isoformat() if t.return_date else None,
            }
            for t in transactions
        ],
    }
