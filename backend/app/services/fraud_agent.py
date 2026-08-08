import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FraudAgent:
    """
    Rule-based fraud / anomaly detection agent.

    Evaluates applicant profile signals that are commonly associated
    with fraudulent loan applications.  Returns a fraud probability
    score (0–100) and a list of triggered flags.

    This agent operates independently of the ML risk model.
    """

    def __init__(self):
        # Thresholds calibrated against common fraud patterns
        self.rules = {
            "age_income_mismatch": {
                "description": "Very high income reported for a young applicant",
                "weight": 20,
            },
            "extreme_loan_to_income": {
                "description": "Requested loan amount vastly exceeds annual income",
                "weight": 25,
            },
            "zero_employment": {
                "description": "No reported employment history",
                "weight": 15,
            },
            "high_grade_no_history": {
                "description": "High-risk loan grade with very short credit history",
                "weight": 20,
            },
            "prior_default": {
                "description": "Applicant has a prior default on record",
                "weight": 20,
            },
        }
        logger.info("FraudAgent initialised with %d detection rules.", len(self.rules))

    def evaluate(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parameters
        ----------
        applicant : dict
            Raw applicant fields (same schema accepted by RiskAgent).

        Returns
        -------
        dict  with keys: fraud_probability, flags, risk_level
        """
        flags = []
        raw_score = 0

        age = applicant.get("person_age", 30)
        income = applicant.get("person_income", 0)
        emp_length = applicant.get("person_emp_length", 0) or 0
        loan_amnt = applicant.get("loan_amnt", 0)
        loan_pct = applicant.get("loan_percent_income", 0)
        grade = applicant.get("loan_grade", "A")
        cred_hist = applicant.get("cb_person_cred_hist_length", 0)
        default_on_file = applicant.get("cb_person_default_on_file", "N")

        # ── Rule 1: Age-income mismatch ─────────────────────────────
        if age < 25 and income > 150_000:
            rule = self.rules["age_income_mismatch"]
            raw_score += rule["weight"]
            flags.append({
                "rule": "age_income_mismatch",
                "detail": (
                    f"Applicant is {age} years old but reports ${income:,.0f} annual "
                    f"income, which is statistically uncommon and warrants verification."
                ),
            })

        # ── Rule 2: Extreme loan-to-income ratio ───────────────────
        if loan_pct > 0.50:
            rule = self.rules["extreme_loan_to_income"]
            raw_score += rule["weight"]
            flags.append({
                "rule": "extreme_loan_to_income",
                "detail": (
                    f"Loan amount of ${loan_amnt:,.0f} represents {loan_pct*100:.1f}% "
                    f"of annual income, exceeding the 50% safety ceiling."
                ),
            })

        # ── Rule 3: Zero employment ────────────────────────────────
        if emp_length == 0:
            rule = self.rules["zero_employment"]
            raw_score += rule["weight"]
            flags.append({
                "rule": "zero_employment",
                "detail": "No current employment history reported on the application.",
            })

        # ── Rule 4: High-risk grade with short credit history ──────
        if grade in ("E", "F", "G") and cred_hist < 3:
            rule = self.rules["high_grade_no_history"]
            raw_score += rule["weight"]
            flags.append({
                "rule": "high_grade_no_history",
                "detail": (
                    f"Loan grade '{grade}' combined with only {cred_hist} years of "
                    f"credit history suggests a thin-file or high-risk profile."
                ),
            })

        # ── Rule 5: Prior default on record ────────────────────────
        if str(default_on_file).upper() == "Y":
            rule = self.rules["prior_default"]
            raw_score += rule["weight"]
            flags.append({
                "rule": "prior_default",
                "detail": "Applicant has a confirmed prior default on their credit file.",
            })

        # Clamp to 0–100
        fraud_probability = min(raw_score, 100)

        if fraud_probability >= 60:
            risk_level = "HIGH"
        elif fraud_probability >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "fraud_probability": fraud_probability,
            "flags": flags,
            "risk_level": risk_level,
        }
