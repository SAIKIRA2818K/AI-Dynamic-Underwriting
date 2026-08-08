import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Will be injected from main.py at startup
orchestrator_instance: Optional[Orchestrator] = None
translation_agent_instance = None

def set_orchestrator(orchestrator: Orchestrator):
    """Called once at application startup to inject the Orchestrator."""
    global orchestrator_instance
    orchestrator_instance = orchestrator

def set_translation_agent(agent):
    """Called once at application startup to inject the TranslationAgent."""
    global translation_agent_instance
    translation_agent_instance = agent


# ── Pydantic Request / Response Models ──────────────────────────────

class TraditionalDataInput(BaseModel):
    person_age: int = Field(..., ge=18, le=100, description="Applicant age in years")
    person_income: float = Field(..., gt=0, description="Annual income in USD")
    person_home_ownership: str = Field(..., description="RENT, MORTGAGE, OWN, or OTHER")
    person_emp_length: Optional[float] = Field(None, ge=0, le=60, description="Employment length in years")
    loan_intent: str = Field(..., description="EDUCATION, MEDICAL, VENTURE, PERSONAL, DEBTCONSOLIDATION, HOMEIMPROVEMENT")
    loan_grade: str = Field(..., description="Loan grade A through G")
    loan_amnt: float = Field(..., gt=0, description="Requested loan amount in USD")
    loan_int_rate: Optional[float] = Field(None, ge=0, description="Interest rate percentage")
    loan_percent_income: float = Field(..., ge=0, le=1, description="Loan amount as fraction of income")
    cb_person_default_on_file: str = Field(..., description="Y or N — prior default on credit file")
    cb_person_cred_hist_length: int = Field(..., ge=0, description="Credit history length in years")

class AlternativeDataInput(BaseModel):
    employment_stability_years: float = Field(0, ge=0, description="Years at current employer")
    linkedin_verified: bool = Field(False, description="Whether LinkedIn profile is verified")
    professional_certifications_count: int = Field(0, ge=0, description="Number of professional certifications")
    utility_bill_consistency_score: float = Field(50, ge=0, le=100, description="Utility bill payment consistency 0-100")
    digital_discipline_score: float = Field(50, ge=0, le=100, description="Digital financial discipline 0-100")

class AnalyzeRequest(BaseModel):
    traditional_data: TraditionalDataInput
    alternative_data: AlternativeDataInput

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "traditional_data": {
                        "person_age": 32,
                        "person_income": 75000,
                        "person_home_ownership": "MORTGAGE",
                        "person_emp_length": 5,
                        "loan_intent": "PERSONAL",
                        "loan_grade": "B",
                        "loan_amnt": 15000,
                        "loan_int_rate": 10.5,
                        "loan_percent_income": 0.20,
                        "cb_person_default_on_file": "N",
                        "cb_person_cred_hist_length": 8,
                    },
                    "alternative_data": {
                        "employment_stability_years": 5,
                        "linkedin_verified": True,
                        "professional_certifications_count": 2,
                        "utility_bill_consistency_score": 92,
                        "digital_discipline_score": 85,
                    },
                }
            ]
        }
    }

class FraudFlag(BaseModel):
    rule: str
    detail: str

class AlternativeBreakdown(BaseModel):
    feature: str
    value: str
    score_impact: float
    max_possible_impact: float
    trust_increase_reason: str
    trust_decrease_reason: str

class AnalyzeResponse(BaseModel):
    risk_score: float = Field(..., description="Creditworthiness score 0-100 (higher = safer)")
    default_probability: float = Field(..., description="Probability of default 0-100")
    risk_label: str = Field(..., description="LOW_RISK, MODERATE_RISK, or HIGH_RISK")
    alternative_score: int = Field(..., description="Alternative trust score 0-100")
    fraud_probability: int = Field(..., description="Fraud probability 0-100")
    fraud_flags: List[FraudFlag] = Field(default_factory=list)
    decision: str = Field(..., description="Approve, Reject, or Manual Review")
    confidence: int = Field(..., description="Decision confidence 0-100")
    reasoning: List[str] = Field(default_factory=list)
    customer_message: str = Field(..., description="Customer-facing explanation")
    bank_summary: str = Field(..., description="Internal bank officer summary")
    recommendations: List[str] = Field(default_factory=list)
    alternative_breakdown: List[AlternativeBreakdown] = Field(default_factory=list)


# ── Endpoint ────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate a loan application",
    description=(
        "Runs the full AI underwriting pipeline: "
        "Risk scoring (LightGBM) → Alternative trust evaluation → "
        "Fraud detection → Decision engine → Explanation generation."
    ),
)
async def analyze_application(request: AnalyzeRequest):
    """Single orchestration endpoint coordinating all AI agents."""
    if orchestrator_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialised. Server is still starting up.",
        )

    try:
        applicant = request.traditional_data.model_dump()
        alt_data = request.alternative_data.model_dump()

        logger.info("POST /analyze — applicant age=%s income=%s", applicant["person_age"], applicant["person_income"])

        result = orchestrator_instance.analyze(applicant, alt_data)
        return result

    except Exception as e:
        logger.exception("Analysis pipeline failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}",
        )

class TranslateRequest(BaseModel):
    target_language: str
    texts: dict

@router.post(
    "/translate",
    status_code=status.HTTP_200_OK,
    summary="Translate explanation texts",
)
async def translate_text(request: TranslateRequest):
    """Translates the customer-facing texts using the TranslationAgent."""
    if translation_agent_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation agent not initialized.",
        )
    
    try:
        translated = translation_agent_instance.translate(
            target_language=request.target_language,
            texts=request.texts
        )
        return translated
    except Exception as e:
        logger.exception("Translation failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}",
        )
