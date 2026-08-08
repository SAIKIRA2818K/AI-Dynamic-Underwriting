import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router, set_orchestrator
from app.services.risk_agent import RiskAgent
from app.services.alternative_data_agent import AlternativeDataAgent
from app.services.fraud_agent import FraudAgent
from app.services.decision_agent import DecisionAgent
from app.services.explanation_agent import ExplanationAgent
from app.services.orchestrator import Orchestrator
from app.services.translation_agent import TranslationAgent

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # backend/
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")          # project root/models/
MODEL_PATH = os.path.join(MODELS_DIR, "risk_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")


# ── Lifespan ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise heavy resources once at startup; tear down on shutdown."""
    logger.info("Starting AI-Driven Dynamic Underwriting System…")

    # Build agents
    risk_agent = RiskAgent(model_path=MODEL_PATH, preprocessor_path=PREPROCESSOR_PATH)
    alternative_agent = AlternativeDataAgent()
    fraud_agent = FraudAgent()
    decision_agent = DecisionAgent()
    explanation_agent = ExplanationAgent()
    translation_agent = TranslationAgent()

    # Wire orchestrator
    orchestrator = Orchestrator(
        risk_agent=risk_agent,
        alternative_agent=alternative_agent,
        fraud_agent=fraud_agent,
        decision_agent=decision_agent,
        explanation_agent=explanation_agent,
    )
    set_orchestrator(orchestrator)
    
    from app.routes.analyze import set_translation_agent
    set_translation_agent(translation_agent)

    logger.info("All agents loaded. Server is ready.")
    yield
    logger.info("Shutting down…")


# ── Application ─────────────────────────────────────────────────────
app = FastAPI(
    title="AI-Driven Dynamic Underwriting System",
    description=(
        "A multi-agent AI system that predicts loan risk using traditional "
        "financial data and alternative digital footprints. Built for the "
        "AI Build 2026 Hackathon."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc alternative
)

# ── CORS ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────
app.include_router(analyze_router, tags=["Underwriting"])


@app.get("/health", tags=["System"], summary="Health check")
async def health_check():
    """Returns server health status and loaded model paths."""
    return {
        "status": "healthy",
        "model_loaded": os.path.exists(MODEL_PATH),
        "preprocessor_loaded": os.path.exists(PREPROCESSOR_PATH),
    }


@app.get("/", tags=["System"], summary="Root")
async def root():
    return {
        "message": "AI-Driven Dynamic Underwriting System API",
        "docs": "/docs",
        "health": "/health",
    }
