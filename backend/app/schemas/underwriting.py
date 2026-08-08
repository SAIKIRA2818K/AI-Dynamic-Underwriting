from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TraditionalData(BaseModel):
    credit_score: int = Field(..., description="Traditional credit score (FICO or similar)")
    annual_income: float = Field(..., description="Applicant annual income")
    debt_to_income_ratio: float = Field(..., description="Debt to income ratio (decimal, e.g. 0.35)")
    employment_duration_months: int = Field(..., description="Duration of current employment in months")
    existing_debts: float = Field(..., description="Total outstanding debts")

class AlternativeData(BaseModel):
    utility_bill_payment_history_rate: float = Field(..., description="Percentage of utility bills paid on time (0.0 to 1.0)")
    rent_payment_history_rate: float = Field(..., description="Percentage of rent payments paid on time (0.0 to 1.0)")
    monthly_transaction_volume: int = Field(..., description="Number of monthly debit/credit card transactions")
    average_monthly_balance: float = Field(..., description="Average bank account balance over 12 months")
    cash_flow_volatility: float = Field(..., description="Cash flow variance or standard deviation")

class UnderwritingRequest(BaseModel):
    applicant_id: str = Field(..., description="Unique identifier for the loan applicant")
    requested_amount: float = Field(..., description="Requested loan amount")
    loan_term_months: int = Field(..., description="Term of loan in months")
    traditional_data: TraditionalData
    alternative_data: AlternativeData

class UnderwritingResponse(BaseModel):
    applicant_id: str
    risk_score: float = Field(..., description="Overall calculated risk score (0.0 low to 1.0 high)")
    decision: str = Field(..., description="Underwriting decision: APPROVED, REJECTED, or MANUAL_REVIEW")
    is_anomaly: bool = Field(..., description="Flag indicating potential fraud or anomalous application details")
    key_risk_factors: list[str] = Field(..., description="Key drivers behind the risk score")
    explanation: str = Field(..., description="AI-generated plain language explanation of the underwriting decision")
    metadata: Optional[Dict[str, Any]] = None
