-- ReturnGuard AI — Database Schema
-- Compatible with PostgreSQL 14+ and SQLite (via SQLAlchemy)

-- =========================================
-- USERS TABLE
-- Stores privacy-safe identity hashes only
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    user_hash       VARCHAR(64) PRIMARY KEY,  -- SHA-256 salted hash of email/phone
    first_seen_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    store_id        VARCHAR(64),               -- Which store the user belongs to (for cross-store matching)
    risk_tier       VARCHAR(10) DEFAULT 'LOW'  -- LOW / MEDIUM / HIGH
);

-- =========================================
-- TRANSACTIONS TABLE
-- Core behavioral fingerprint data store
-- =========================================
CREATE TABLE IF NOT EXISTS transactions (
    id                  SERIAL PRIMARY KEY,
    user_hash           VARCHAR(64) NOT NULL REFERENCES users(user_hash) ON DELETE CASCADE,
    action_type         VARCHAR(20) NOT NULL,  -- View | AddToCart | Purchase | ReturnRequest
    timestamp           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_value         DECIMAL(10, 2),        -- In INR/USD
    product_category    VARCHAR(100),          -- e.g., Clothing, Electronics, Footwear
    product_id          VARCHAR(64),           -- SKU or product identifier
    size_variant        VARCHAR(20),           -- S, M, L, XL, 32, etc.
    delivery_date       TIMESTAMP,             -- When the product was delivered (for Temporal Gap calc)
    return_date         TIMESTAMP,             -- When the return was requested
    order_id            VARCHAR(64)            -- Groups Purchase + ReturnRequest for same order
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_hash ON transactions(user_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_action_type ON transactions(action_type);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);

-- =========================================
-- RISK SCORES TABLE
-- Cached scores to avoid recomputing on every request
-- =========================================
CREATE TABLE IF NOT EXISTS risk_scores (
    id              SERIAL PRIMARY KEY,
    user_hash       VARCHAR(64) NOT NULL REFERENCES users(user_hash),
    risk_score      DECIMAL(5, 2) NOT NULL,       -- 0.00 to 100.00
    risk_level      VARCHAR(10) NOT NULL,          -- LOW / MEDIUM / HIGH
    reason_codes    TEXT,                          -- JSON array of flag codes
    computed_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_version   VARCHAR(20) DEFAULT 'v1.0'
);

CREATE INDEX IF NOT EXISTS idx_risk_scores_user_hash ON risk_scores(user_hash);
