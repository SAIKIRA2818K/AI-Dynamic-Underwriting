import json
from typing import Dict, Any, List

class AlternativeDataAgent:
    """
    Independent Agent evaluating borrower credit trustworthiness using alternative non-traditional data streams.
    Does not depend on the primary ML default model.
    """
    
    def __init__(self):
        # Weight distributions summing up to 1.0 (100 points)
        self.weights = {
            "employment_stability": 0.20,      # Weight: 20%
            "linkedin_verified": 0.15,         # Weight: 15%
            "professional_certifications": 0.15, # Weight: 15%
            "utility_bill_consistency": 0.25,  # Weight: 25%
            "digital_discipline": 0.25          # Weight: 25%
        }

    def evaluate_trust(
        self,
        employment_stability_years: float,
        linkedin_verified: bool,
        professional_certifications_count: int,
        utility_bill_consistency_score: float,
        digital_discipline_score: float
    ) -> Dict[str, Any]:
        """
        Orchestrates alternative data scoring and feature explanation.
        
        Parameters:
        - employment_stability_years: Duration in current position.
        - linkedin_verified: Verification status of professional profile.
        - professional_certifications_count: Count of active industry credentials.
        - utility_bill_consistency_score: Punctuality index of bill payments (0-100).
        - digital_discipline_score: Transactional cash buffer and budget compliance score (0-100).
        """
        # 1. Feature scoring calculations (mapped to 0-100 individual scale)
        emp_score = min(employment_stability_years / 5.0, 1.0) * 100  # Cap maximum rating at 5+ years
        li_score = 100.0 if linkedin_verified else 0.0
        cert_score = min(professional_certifications_count / 3.0, 1.0) * 100  # Cap maximum rating at 3+ credentials
        utility_score = max(0.0, min(utility_bill_consistency_score, 100.0))
        discipline_score = max(0.0, min(digital_discipline_score, 100.0))

        # 2. Weighted score accumulation
        weighted_score = (
            (emp_score * self.weights["employment_stability"]) +
            (li_score * self.weights["linkedin_verified"]) +
            (cert_score * self.weights["professional_certifications"]) +
            (utility_score * self.weights["utility_bill_consistency"]) +
            (discipline_score * self.weights["digital_discipline"])
        )
        alternative_score = int(round(weighted_score))

        # 3. Explanations and feature breakdown assembly
        feature_breakdown = [
            {
                "feature": "Employment Stability",
                "value": f"{employment_stability_years} years",
                "score_impact": round(emp_score * self.weights["employment_stability"], 2),
                "max_possible_impact": round(100 * self.weights["employment_stability"], 2),
                "trust_increase_reason": (
                    "Long-term tenure in a single organization indicates career stability, "
                    "reliable salary flows, and lower vulnerability to sudden income disruption."
                ),
                "trust_decrease_reason": (
                    "Short employment tenure or high frequency of job changes can indicate career instability, "
                    "onboarding probation risks, and potential disruptions in income streams."
                )
            },
            {
                "feature": "LinkedIn Verification",
                "value": "Verified" if linkedin_verified else "Not Verified",
                "score_impact": round(li_score * self.weights["linkedin_verified"], 2),
                "max_possible_impact": round(100 * self.weights["linkedin_verified"], 2),
                "trust_increase_reason": (
                    "A verified professional profile confirms digital presence, helps validate "
                    "employment credentials, and significantly mitigates the risk of identity theft/fraud."
                ),
                "trust_decrease_reason": (
                    "Unverified digital profiles increase identity validation friction and present "
                    "a higher risk profile regarding credential exaggeration or fabricated applications."
                )
            },
            {
                "feature": "Professional Certifications",
                "value": f"{professional_certifications_count} credentials",
                "score_impact": round(cert_score * self.weights["professional_certifications"], 2),
                "max_possible_impact": round(100 * self.weights["professional_certifications"], 2),
                "trust_increase_reason": (
                    "Active industry certifications show skill progression, dedication to career advancement, "
                    "and higher employability/demand in the job market during economic contractions."
                ),
                "trust_decrease_reason": (
                    "A lack of active professional credentials may indicate stagnant skill progression, "
                    "making the applicant relatively more vulnerable to layoffs during downturns."
                )
            },
            {
                "feature": "Utility Bill Punctuality",
                "value": f"{utility_bill_consistency_score}/100",
                "score_impact": round(utility_score * self.weights["utility_bill_consistency"], 2),
                "max_possible_impact": round(100 * self.weights["utility_bill_consistency"], 2),
                "trust_increase_reason": (
                    "Consistent on-time utility payments demonstrate excellent personal organization, financial "
                    "discipline, and a strong history of prioritizing recurring legal agreements."
                ),
                "trust_decrease_reason": (
                    "Low billing compliance index shows budget stress, mismanagement of recurring "
                    "priorities, or insufficient liquidity buffers to cover basic monthly obligations."
                )
            },
            {
                "feature": "Digital Financial Discipline",
                "value": f"{digital_discipline_score}/100",
                "score_impact": round(discipline_score * self.weights["digital_discipline"], 2),
                "max_possible_impact": round(100 * self.weights["digital_discipline"], 2),
                "trust_increase_reason": (
                    "High digital budget discipline represents proactive savings habits, controlled impulse spending, "
                    "and the presence of healthy cash buffers to absorb emergency expenses."
                ),
                "trust_decrease_reason": (
                    "Weak digital discipline scores suggest volatile transactional behaviors, low "
                    "budget compliance, and higher probability of living paycheck-to-paycheck."
                )
            }
        ]

        # 4. Formulate recommendations based on trust score brackets
        if alternative_score >= 80:
            recommendation = (
                "EXCELLENT TRUST PROFILE: Alternative data shows exceptional character and financial discipline. "
                "Strongly recommend for interest rate discounts or expedited automated underwriting approval."
            )
            confidence = 0.95
        elif alternative_score >= 60:
            recommendation = (
                "GOOD TRUST PROFILE: Borrower displays solid consistency across most alternative indicators. "
                "Suitable for standard loan products; proceed with normal verification processes."
            )
            confidence = 0.85
        elif alternative_score >= 40:
            recommendation = (
                "FAIR TRUST PROFILE: Mixed results in cash management or employment stability. "
                "Recommend adding secondary verification streams or applying a minor interest rate premium."
            )
            confidence = 0.75
        else:
            recommendation = (
                "HIGH RISK PROFILE: Alternative metrics flag multiple red flags in payment behavior or stability. "
                "Recommend rejection or forwarding to intensive manual underwriting review."
            )
            confidence = 0.65

        # 5. Build output dictionary
        return {
            "alternative_score": alternative_score,
            "feature_breakdown": feature_breakdown,
            "recommendation": recommendation,
            "confidence": confidence
        }

if __name__ == "__main__":
    # Test script run to demonstrate the agent independent capability
    agent = AlternativeDataAgent()
    test_result = agent.evaluate_trust(
        employment_stability_years=3.5,
        linkedin_verified=True,
        professional_certifications_count=2,
        utility_bill_consistency_score=92.0,
        digital_discipline_score=80.0
    )
    print(json.dumps(test_result, indent=2))
