import os
import logging
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RiskAgent:
    """
    Wraps the trained LightGBM credit risk model and the fitted
    preprocessor pipeline.  Accepts raw applicant data, transforms it,
    runs inference, and returns a normalised risk score (0–100).
    """

    def __init__(self, model_path: str, preprocessor_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Risk model not found: {model_path}")
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found: {preprocessor_path}")

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        logger.info("RiskAgent initialised — model and preprocessor loaded.")

    def predict(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parameters
        ----------
        applicant : dict
            Raw applicant fields matching the original CSV schema:
            person_age, person_income, person_home_ownership,
            person_emp_length, loan_intent, loan_grade, loan_amnt,
            loan_int_rate, loan_percent_income,
            cb_person_default_on_file, cb_person_cred_hist_length

        Returns
        -------
        dict  with keys: risk_score, default_probability, risk_label
        """
        # Build a single-row DataFrame matching the raw CSV columns
        raw_df = pd.DataFrame([{
            "person_age": applicant["person_age"],
            "person_income": applicant["person_income"],
            "person_home_ownership": applicant["person_home_ownership"],
            "person_emp_length": applicant["person_emp_length"],
            "loan_intent": applicant["loan_intent"],
            "loan_grade": applicant["loan_grade"],
            "loan_amnt": applicant["loan_amnt"],
            "loan_int_rate": applicant["loan_int_rate"],
            "loan_percent_income": applicant["loan_percent_income"],
            "cb_person_default_on_file": applicant["cb_person_default_on_file"],
            "cb_person_cred_hist_length": applicant["cb_person_cred_hist_length"],
        }])

        # Transform using the fitted preprocessor (same pipeline as training)
        processed_df = self._transform(raw_df)

        # Predict probability of default (class 1)
        default_prob = float(self.model.predict_proba(processed_df)[0][1])

        # Convert to a 0–100 "creditworthiness" score (higher = safer)
        risk_score = round((1 - default_prob) * 100, 2)

        if risk_score >= 80:
            risk_label = "LOW_RISK"
        elif risk_score >= 60:
            risk_label = "MODERATE_RISK"
        else:
            risk_label = "HIGH_RISK"

        return {
            "risk_score": risk_score,
            "default_probability": round(default_prob * 100, 2),
            "risk_label": risk_label,
        }

    # ── Private ─────────────────────────────────────────────────────

    def _transform(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Applies the same preprocessing pipeline used during training."""
        pp = self.preprocessor
        df = raw_df.copy()

        # 1. Imputation
        for col, val in pp["medians"].items():
            if col in df.columns:
                df[col] = df[col].fillna(val)

        # 2. Manual ordinal & binary mappings
        df["loan_grade_encoded"] = df["loan_grade"].map(
            {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
        ).fillna(-1)

        df["cb_person_default_on_file_encoded"] = df["cb_person_default_on_file"].map(
            {"Y": 1, "N": 0}
        ).fillna(0)

        # 3. One-hot encoding
        ohe_data = pp["ohe"].transform(df[pp["cat_cols"]])
        ohe_df = pd.DataFrame(ohe_data, columns=pp["ohe_feature_names"], index=df.index)

        # 4. Assemble numeric block
        numeric = pd.DataFrame(index=df.index)
        for col in pp["num_cols"]:
            numeric[col] = df[col]
        numeric["loan_grade_encoded"] = df["loan_grade_encoded"]
        numeric["cb_person_default_on_file_encoded"] = df["cb_person_default_on_file_encoded"]

        features = pd.concat([numeric, ohe_df], axis=1)

        # 5. Scale
        scaled = pp["scaler"].transform(features)
        return pd.DataFrame(scaled, columns=pp["feature_names_out"], index=df.index)
