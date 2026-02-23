"""
ReturnGuard AI — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import init_db
from services import model_service
from routes import transactions, risk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup & shutdown events."""
    logger.info("🚀 ReturnGuard AI starting up...")
    # Initialize database (create tables)
    await init_db()
    logger.info("✅ Database initialized")
    # Load ML model
    model_service.load_model(settings.model_path, settings.feature_names_path)
    yield
    logger.info("🛑 ReturnGuard AI shutting down...")


app = FastAPI(
    title="ReturnGuard AI — Fraud Detection API",
    description=(
        "Patent-grade behavioral fingerprinting system for e-commerce return fraud detection. "
        "Uses XGBoost + SMOTE + Salted Hashing to generate real-time risk scores."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the React frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(transactions.router)
app.include_router(risk.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "ReturnGuard AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "model_loaded": model_service._model is not None,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
