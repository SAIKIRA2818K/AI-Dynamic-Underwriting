import json
from typing import Dict, Any, List


class DecisionAgent:
    """
    Final-stage orchestrator that fuses signals from the Risk Model,
    Alternative Data Agent, and Fraud Detection layer into a single
    underwriting verdict.

    Operates independently — no dependency on the frontend or any
    specific ML model internals.
    """

    # ── Decision Constants ──────────────────────────────────────────
    DECISION_APPROVE = "Approve"
    DECISION_REJECT = "Reject"
    DECISION_MANUAL_REVIEW = "Manual Review"

    # ── Threshold Configuration ─────────────────────────────────────
    FRAUD_REJECT_THRESHOLD = 70        # Fraud probability above this → instant reject
    RISK_HIGH_THRESHOLD = 80           # Risk score above this is considered high-confidence
    RISK_MODERATE_LOW = 60             # Risk score between 60–80 → manual review band
    ALTERNATIVE_TRUST_THRESHOLD = 70   # Alternative trust must exceed this for approval

    def decide(
        self,
        financial_risk_score: float,
        alternative_trust_score: float,
        fraud_probability: float,
    ) -> Dict[str, Any]:
        """
        Evaluates the three input signals against business rules and
        returns a structured underwriting decision.

        Parameters
        ----------
        financial_risk_score : float
            ML model output representing creditworthiness (0 = high risk, 100 = low risk).
        alternative_trust_score : float
            Alternative Data Agent output (0–100).
        fraud_probability : float
            Fraud / anomaly detection probability (0–100).

        Returns
        -------
        dict  with keys: decision, confidence, reasoning
        """
        # Clamp inputs to valid range
        financial_risk_score = max(0.0, min(float(financial_risk_score), 100.0))
        alternative_trust_score = max(0.0, min(float(alternative_trust_score), 100.0))
        fraud_probability = max(0.0, min(float(fraud_probability), 100.0))

        reasoning: List[str] = []

        # ── Rule 1: Fraud Gate (highest priority) ───────────────────
        if fraud_probability > self.FRAUD_REJECT_THRESHOLD:
            decision = self.DECISION_REJECT
            reasoning.append(
                f"Fraud probability is {fraud_probability:.1f}%, which exceeds "
                f"the safety threshold of {self.FRAUD_REJECT_THRESHOLD}%. "
                f"Application is automatically rejected to protect against potential fraud."
            )
            reasoning.append(
                "This decision overrides all other scoring signals as fraud "
                "prevention is the highest-priority business rule."
            )
            confidence = self._compute_confidence(
                decision, financial_risk_score, alternative_trust_score, fraud_probability
            )
            return self._build_response(decision, confidence, reasoning)

        # ── Rule 2: Approve — strong risk + strong trust ────────────
        if (
            financial_risk_score > self.RISK_HIGH_THRESHOLD
            and alternative_trust_score > self.ALTERNATIVE_TRUST_THRESHOLD
        ):
            decision = self.DECISION_APPROVE
            reasoning.append(
                f"Financial risk score of {financial_risk_score:.1f} exceeds the "
                f"high-confidence threshold of {self.RISK_HIGH_THRESHOLD}, indicating "
                f"strong creditworthiness based on traditional data."
            )
            reasoning.append(
                f"Alternative trust score of {alternative_trust_score:.1f} exceeds "
                f"the minimum trust threshold of {self.ALTERNATIVE_TRUST_THRESHOLD}, "
                f"confirming positive signals from non-traditional data sources "
                f"(employment stability, utility payments, digital discipline)."
            )
            reasoning.append(
                f"Fraud probability is low at {fraud_probability:.1f}%, well within "
                f"acceptable safety limits."
            )
            confidence = self._compute_confidence(
                decision, financial_risk_score, alternative_trust_score, fraud_probability
            )
            return self._build_response(decision, confidence, reasoning)

        # ── Rule 3: Manual Review — moderate risk band ──────────────
        if self.RISK_MODERATE_LOW <= financial_risk_score <= self.RISK_HIGH_THRESHOLD:
            decision = self.DECISION_MANUAL_REVIEW
            reasoning.append(
                f"Financial risk score of {financial_risk_score:.1f} falls within the "
                f"moderate assessment band ({self.RISK_MODERATE_LOW}–{self.RISK_HIGH_THRESHOLD}), "
                f"which requires human underwriter verification."
            )
            if alternative_trust_score > self.ALTERNATIVE_TRUST_THRESHOLD:
                reasoning.append(
                    f"Alternative trust score of {alternative_trust_score:.1f} is favorable "
                    f"and may support approval upon manual review."
                )
            else:
                reasoning.append(
                    f"Alternative trust score of {alternative_trust_score:.1f} is below "
                    f"the preferred threshold of {self.ALTERNATIVE_TRUST_THRESHOLD}, adding "
                    f"further justification for manual verification."
                )
            reasoning.append(
                f"Fraud probability is {fraud_probability:.1f}%, within acceptable range. "
                f"A human underwriter should validate documentation before final approval."
            )
            confidence = self._compute_confidence(
                decision, financial_risk_score, alternative_trust_score, fraud_probability
            )
            return self._build_response(decision, confidence, reasoning)

        # ── Rule 4: Reject — catch-all for remaining cases ──────────
        decision = self.DECISION_REJECT
        reasoning.append(
            f"Financial risk score of {financial_risk_score:.1f} is below the minimum "
            f"threshold of {self.RISK_MODERATE_LOW}, indicating high probability of default."
        )
        if alternative_trust_score <= self.ALTERNATIVE_TRUST_THRESHOLD:
            reasoning.append(
                f"Alternative trust score of {alternative_trust_score:.1f} does not "
                f"compensate for the weak financial profile, as it falls below "
                f"the trust threshold of {self.ALTERNATIVE_TRUST_THRESHOLD}."
            )
        else:
            reasoning.append(
                f"Although the alternative trust score of {alternative_trust_score:.1f} "
                f"is positive, it is insufficient to override the low financial risk score."
            )
        reasoning.append(
            "The application does not meet the minimum criteria for approval "
            "or manual review under current underwriting policy."
        )
        confidence = self._compute_confidence(
            decision, financial_risk_score, alternative_trust_score, fraud_probability
        )
        return self._build_response(decision, confidence, reasoning)

    # ── Private Helpers ─────────────────────────────────────────────

    def _compute_confidence(
        self,
        decision: str,
        risk: float,
        trust: float,
        fraud: float,
    ) -> int:
        """
        Derives a confidence percentage (0–100) reflecting how strongly
        the input signals align with the chosen decision.
        """
        if decision == self.DECISION_REJECT and fraud > self.FRAUD_REJECT_THRESHOLD:
            # High fraud → very high confidence in rejection
            return min(99, int(50 + fraud * 0.5))

        if decision == self.DECISION_APPROVE:
            # Confidence rises with higher risk score, higher trust, lower fraud
            raw = (risk * 0.45) + (trust * 0.35) + ((100 - fraud) * 0.20)
            return min(99, int(raw))

        if decision == self.DECISION_MANUAL_REVIEW:
            # Moderate confidence — closer to thresholds means less certainty
            distance_from_center = abs(risk - 70) / 10  # 0–1 within band
            raw = 60 + (trust * 0.15) + (distance_from_center * 10)
            return min(90, int(raw))

        # Default reject confidence
        raw = 50 + ((100 - risk) * 0.3) + ((100 - trust) * 0.2)
        return min(95, int(raw))

    @staticmethod
    def _build_response(
        decision: str,
        confidence: int,
        reasoning: List[str],
    ) -> Dict[str, Any]:
        """Assembles the standardized output dictionary."""
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
        }


# ── Self-test scenarios ─────────────────────────────────────────────
if __name__ == "__main__":
    agent = DecisionAgent()

    scenarios = [
        {
            "label": "Strong Approve",
            "financial_risk_score": 92,
            "alternative_trust_score": 84,
            "fraud_probability": 5,
        },
        {
            "label": "Fraud Reject",
            "financial_risk_score": 88,
            "alternative_trust_score": 90,
            "fraud_probability": 85,
        },
        {
            "label": "Manual Review",
            "financial_risk_score": 72,
            "alternative_trust_score": 65,
            "fraud_probability": 15,
        },
        {
            "label": "Low Score Reject",
            "financial_risk_score": 40,
            "alternative_trust_score": 55,
            "fraud_probability": 10,
        },
    ]

    for scenario in scenarios:
        label = scenario.pop("label")
        result = agent.decide(**scenario)
        print(f"\n{'='*60}")
        print(f"  Scenario: {label}")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2))
