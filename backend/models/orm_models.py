from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db import Base


class User(Base):
    __tablename__ = "users"

    user_hash = Column(String(64), primary_key=True, index=True)
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    store_id = Column(String(64), nullable=True)
    risk_tier = Column(String(10), default="LOW")

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    risk_scores = relationship("RiskScore", back_populates="user", cascade="all, delete")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_hash = Column(String(64), ForeignKey("users.user_hash", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(20), nullable=False)   # View | AddToCart | Purchase | ReturnRequest
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    order_value = Column(Numeric(10, 2), nullable=True)
    product_category = Column(String(100), nullable=True)
    product_id = Column(String(64), nullable=True)
    size_variant = Column(String(20), nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)
    order_id = Column(String(64), nullable=True)

    user = relationship("User", back_populates="transactions")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_hash = Column(String(64), ForeignKey("users.user_hash", ondelete="CASCADE"), nullable=False, index=True)
    risk_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(String(10), nullable=False)   # LOW | MEDIUM | HIGH
    reason_codes = Column(Text, nullable=True)         # JSON array stored as text
    computed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    model_version = Column(String(20), default="v1.0")

    user = relationship("User", back_populates="risk_scores")
