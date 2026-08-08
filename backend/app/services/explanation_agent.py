import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env"))

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ── Modular Prompt Templates ───────────────────────────────────────

SYSTEM_PROMPT = (
    "You are the Explanation Agent for an AI-powered bank underwriting system. "
    "Your role is to translate raw machine-generated risk assessments into clear, "
    "empathetic, and professional language that both customers and bank officers "
    "can understand. Never reveal internal score thresholds, model names, or "
    "technical implementation details."
)

CUSTOMER_MESSAGE_PROMPT = (
    "Based on the underwriting decision below, write a short customer-facing message "
    "(maximum 100 words). Be warm, professional, and clear. If the loan is approved, "
    "congratulate the applicant. If rejected, be empathetic and encouraging. If sent "
    "to manual review, explain that additional verification is needed.\n\n"
    "Decision Data:\n{decision_json}\n\n"
    "Respond with ONLY the customer message text, no headers or labels."
)

RECOMMENDATIONS_PROMPT = (
    "Based on the underwriting decision below, provide exactly 3 short, personalized, "
    "actionable recommendations the applicant can follow to improve their future loan "
    "eligibility. Each recommendation should be 1-2 sentences. Focus on practical "
    "financial habits, not generic advice.\n\n"
    "Decision Data:\n{decision_json}\n\n"
    "Respond with ONLY a JSON array of 3 strings. Example:\n"
    '[\"Recommendation 1\", \"Recommendation 2\", \"Recommendation 3\"]'
)

BANK_SUMMARY_PROMPT = (
    "Based on the underwriting decision below, write a concise internal summary "
    "for a bank loan officer (3-4 sentences). Include the risk assessment, the "
    "alternative trust evaluation, fraud status, and the final verdict. Use "
    "professional banking terminology.\n\n"
    "Decision Data:\n{decision_json}\n\n"
    "Respond with ONLY the bank summary text, no headers or labels."
)


# ── Fallback Generator (no API key / offline mode) ─────────────────

def _generate_fallback(decision_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces deterministic, template-based explanations when the
    OpenAI API is unavailable (missing key, network issues, etc.).
    """
    decision = decision_data.get("decision", "Unknown")
    risk = decision_data.get("risk_score", 0)
    alt = decision_data.get("alternative_score", 0)
    fraud = decision_data.get("fraud_probability", 0)
    confidence = decision_data.get("confidence", 0)
    reasoning_list: List[str] = decision_data.get("reasoning", [])
    reasoning_text = " ".join(reasoning_list)

    # Customer message
    if decision == "Approve":
        customer_message = (
            f"Congratulations! Your loan application has been approved with a confidence "
            f"level of {confidence}%. Our assessment found strong financial indicators "
            f"and positive alternative data signals supporting your creditworthiness. "
            f"You will receive detailed terms and next steps shortly."
        )
    elif decision == "Manual Review":
        customer_message = (
            f"Thank you for your application. Based on our initial assessment, your "
            f"application requires additional verification by our underwriting team. "
            f"This is a standard procedure and does not indicate rejection. A loan officer "
            f"will contact you within 2-3 business days with an update."
        )
    else:
        customer_message = (
            f"Thank you for your interest in our loan products. After careful review, "
            f"we are unable to approve your application at this time. We encourage you "
            f"to review your financial profile and consider reapplying in the future. "
            f"Our team is available to help you understand the steps you can take."
        )

    # Bank summary
    bank_summary = (
        f"Applicant evaluated with a financial risk score of {risk}/100 and an "
        f"alternative trust score of {alt}/100. Fraud probability assessed at "
        f"{fraud}%. Final decision: {decision} (confidence: {confidence}%). "
        f"Reasoning: {reasoning_text}"
    )

    # Recommendations
    if decision == "Approve":
        recommendations = [
            "Continue maintaining your strong payment history to qualify for premium rate offers in the future.",
            "Consider diversifying your savings across multiple instruments to further strengthen your financial profile.",
            "Keep your debt-to-income ratio below 35% to maintain eligibility for higher credit limits."
        ]
    elif decision == "Manual Review":
        recommendations = [
            "Ensure all employment and income documentation is current and readily available for the reviewing officer.",
            "Improving your utility bill payment consistency above 90% can positively influence future automated approvals.",
            "Consider adding a verified LinkedIn profile or professional certifications to strengthen your alternative data score."
        ]
    else:
        recommendations = [
            "Focus on building a consistent payment history over the next 6-12 months before reapplying.",
            "Reduce your existing debt obligations to lower your debt-to-income ratio below 40%.",
            "Establish digital financial discipline by maintaining a stable average monthly balance in your primary account."
        ]

    return {
        "customer_message": customer_message,
        "bank_summary": bank_summary,
        "recommendations": recommendations,
    }


# ── Main Agent Class ───────────────────────────────────────────────

class ExplanationAgent:
    """
    Converts structured underwriting decisions into human-readable
    explanations using the OpenAI API, with a robust offline fallback.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.client = None

        if OPENAI_AVAILABLE and self.api_key and self.api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=self.api_key)
            print(f"[ExplanationAgent] OpenAI client initialized (model: {self.model})")
        else:
            reason = "openai package not installed" if not OPENAI_AVAILABLE else "API key not configured"
            print(f"[ExplanationAgent] Running in OFFLINE fallback mode ({reason})")

    def _call_openai(self, user_prompt: str) -> str:
        """Makes a single chat completion call and returns the response text."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    def explain(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates all three explanation components for a given decision.

        Parameters
        ----------
        decision_data : dict
            Must contain: risk_score, alternative_score, fraud_probability,
            decision, confidence, reasoning.

        Returns
        -------
        dict with keys: customer_message, bank_summary, recommendations
        """
        # If OpenAI client is not available, use deterministic fallback
        if self.client is None:
            return _generate_fallback(decision_data)

        decision_json = json.dumps(decision_data, indent=2)

        try:
            # 1. Customer message
            customer_message = self._call_openai(
                CUSTOMER_MESSAGE_PROMPT.format(decision_json=decision_json)
            )

            # 2. Recommendations
            raw_recommendations = self._call_openai(
                RECOMMENDATIONS_PROMPT.format(decision_json=decision_json)
            )
            try:
                recommendations = json.loads(raw_recommendations)
                if not isinstance(recommendations, list):
                    raise ValueError
            except (json.JSONDecodeError, ValueError):
                # If the LLM didn't return valid JSON, split by newlines
                recommendations = [
                    line.strip().lstrip("0123456789.-) ")
                    for line in raw_recommendations.split("\n")
                    if line.strip()
                ][:3]

            # 3. Bank summary
            bank_summary = self._call_openai(
                BANK_SUMMARY_PROMPT.format(decision_json=decision_json)
            )

            return {
                "customer_message": customer_message,
                "bank_summary": bank_summary,
                "recommendations": recommendations,
            }

        except Exception as e:
            print(f"[ExplanationAgent] OpenAI call failed: {e}. Using fallback.")
            return _generate_fallback(decision_data)


# ── Self-test ──────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = ExplanationAgent()

    sample_decision = {
        "risk_score": 82,
        "alternative_score": 88,
        "fraud_probability": 7,
        "decision": "Approve",
        "confidence": 94,
        "reasoning": [
            "Financial risk score of 82.0 exceeds the high-confidence threshold of 80, indicating strong creditworthiness based on traditional data.",
            "Alternative trust score of 88.0 exceeds the minimum trust threshold of 70, confirming positive signals from non-traditional data sources.",
            "Fraud probability is low at 7.0%, well within acceptable safety limits."
        ],
    }

    result = agent.explain(sample_decision)
    print(json.dumps(result, indent=2))
