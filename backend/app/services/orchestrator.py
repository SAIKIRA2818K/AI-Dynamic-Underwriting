import logging
from typing import Dict, Any

from app.services.risk_agent import RiskAgent
from app.services.alternative_data_agent import AlternativeDataAgent
from app.services.fraud_agent import FraudAgent
from app.services.decision_agent import DecisionAgent
from app.services.explanation_agent import ExplanationAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central coordination layer that chains every AI agent in the
    correct sequence and merges their outputs into a single response.

    Pipeline:
        1. RiskAgent        → financial risk score (LightGBM)
        2. AlternativeDataAgent → alternative trust score
        3. FraudAgent       → fraud probability
        4. DecisionAgent    → final decision + reasoning
        5. ExplanationAgent → customer message + bank summary + recommendations
    """

    def __init__(
        self,
        risk_agent: RiskAgent,
        alternative_agent: AlternativeDataAgent,
        fraud_agent: FraudAgent,
        decision_agent: DecisionAgent,
        explanation_agent: ExplanationAgent,
    ):
        self.risk_agent = risk_agent
        self.alternative_agent = alternative_agent
        self.fraud_agent = fraud_agent
        self.decision_agent = decision_agent
        self.explanation_agent = explanation_agent
        logger.info("Orchestrator initialised — all agents connected.")

    def analyze(self, applicant: Dict[str, Any], alternative_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full underwriting pipeline for one applicant.

        Parameters
        ----------
        applicant : dict
            Traditional financial fields (person_age, person_income, …).
        alternative_data : dict
            Non-traditional trust signals (employment_stability_years,
            linkedin_verified, professional_certifications_count,
            utility_bill_consistency_score, digital_discipline_score).

        Returns
        -------
        dict  Unified JSON response for the API.
        """
        # ── Step 1: ML Risk Scoring ─────────────────────────────────
        logger.info("Step 1/5 — Running RiskAgent (LightGBM)…")
        risk_result = self.risk_agent.predict(applicant)

        # ── Step 2: Alternative Data Scoring ────────────────────────
        logger.info("Step 2/5 — Running AlternativeDataAgent…")
        alt_result = self.alternative_agent.evaluate_trust(
            employment_stability_years=alternative_data.get("employment_stability_years", 0),
            linkedin_verified=alternative_data.get("linkedin_verified", False),
            professional_certifications_count=alternative_data.get("professional_certifications_count", 0),
            utility_bill_consistency_score=alternative_data.get("utility_bill_consistency_score", 0),
            digital_discipline_score=alternative_data.get("digital_discipline_score", 0),
        )

        # ── Step 3: Fraud Detection ────────────────────────────────
        logger.info("Step 3/5 — Running FraudAgent…")
        fraud_result = self.fraud_agent.evaluate(applicant)

        # ── Step 4: Decision ───────────────────────────────────────
        logger.info("Step 4/5 — Running DecisionAgent…")
        decision_result = self.decision_agent.decide(
            financial_risk_score=risk_result["risk_score"],
            alternative_trust_score=alt_result["alternative_score"],
            fraud_probability=fraud_result["fraud_probability"],
        )

        # ── Step 5: Explanation ────────────────────────────────────
        logger.info("Step 5/5 — Running ExplanationAgent…")
        explanation_input = {
            "risk_score": risk_result["risk_score"],
            "alternative_score": alt_result["alternative_score"],
            "fraud_probability": fraud_result["fraud_probability"],
            "decision": decision_result["decision"],
            "confidence": decision_result["confidence"],
            "reasoning": decision_result["reasoning"],
        }
        explanation_result = self.explanation_agent.explain(explanation_input)

        # ── Merge all outputs ──────────────────────────────────────
        logger.info("Pipeline complete — merging results.")
        return {
            # Core scores
            "risk_score": risk_result["risk_score"],
            "default_probability": risk_result["default_probability"],
            "risk_label": risk_result["risk_label"],
            "alternative_score": alt_result["alternative_score"],
            "fraud_probability": fraud_result["fraud_probability"],
            "fraud_flags": fraud_result["flags"],
            # Decision
            "decision": decision_result["decision"],
            "confidence": decision_result["confidence"],
            "reasoning": decision_result["reasoning"],
            # Explanations
            "customer_message": explanation_result["customer_message"],
            "bank_summary": explanation_result["bank_summary"],
            "recommendations": explanation_result["recommendations"],
            # Detailed breakdowns (for frontend charts)
            "alternative_breakdown": alt_result["feature_breakdown"],
        }
