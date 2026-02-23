# 🛡️ ReturnGuard AI — Return Fraud Detection System

A patent-grade AI system that generates **Behavioral Fingerprints** to detect e-commerce return fraud in real time.

## Architecture

```
┌─────────────────────┐     POST /v1/get-risk-score     ┌─────────────────────┐
│   React Dashboard   │ ────────────────────────────►  │   FastAPI Backend   │
│  (Vite + CSS)       │ ◄────────────────────────────   │  + XGBoost Model    │
└─────────────────────┘       { risk_score: 0-100 }     └──────────┬──────────┘
                                                                    │
                                                         ┌──────────▼──────────┐
                                                         │  SQLite / PostgreSQL │
                                                         │  Transaction Logs    │
                                                         └─────────────────────┘
```

## Features

- **Behavioral Fingerprints**: Return-to-Purchase Ratio, Temporal Gap, Size-Variation Flag
- **Privacy Layer**: Salted SHA-256 hashing for cross-store identity matching
- **SMOTE**: Synthetic Minority Over-sampling for imbalanced fraud datasets
- **XGBoost**: Gradient Boosting classifier with Feature Importance reporting
- **Dynamic UI**: COD payment option hidden for users with risk score > 80

## Quick Start

### 1. Train the ML Model
```bash
cd ml
pip install -r requirements.txt
python generate_data.py
python feature_engineering.py
python train_model.py
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18, Vite, Axios               |
| Backend    | Python 3.11, FastAPI, SQLAlchemy    |
| Database   | SQLite (dev) / PostgreSQL (prod)    |
| ML         | XGBoost, scikit-learn, imbalanced-learn, SMOTE |
| Privacy    | Salted SHA-256 Hashing              |

## API Reference

### `POST /v1/get-risk-score`
```json
// Request
{ "user_hash": "abc123...", "cart": [{ "product_id": "P1", "category": "Clothing", "size": "L", "value": 1299 }] }

// Response
{ "risk_score": 87, "risk_level": "HIGH", "reason_codes": ["high_return_ratio", "size_variation_detected"] }
```

### `POST /v1/log-action`
```json
{ "user_hash": "abc123...", "action_type": "Purchase", "product_id": "P1", "product_category": "Clothing", "order_value": 1299, "size_variant": "L" }
```
