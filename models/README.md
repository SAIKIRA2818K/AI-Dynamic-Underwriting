# Machine Learning Models Directory

This folder is used to store serialized machine learning model binaries and metadata.

## Structure
- `xgboost_risk_model.json`: The trained XGBoost model for predicting default risk.
- `anomaly_detector.joblib`: The trained Isolation Forest model for outlier/fraud detection on bank cash flows.
- `scaler.joblib`: The Scikit-learn scaler or preprocessor pipelines used for data normalization.

## Workflow
1. Models are trained offline or via training scripts in the `utils/` directory.
2. Serialized model assets are saved here.
3. The FastAPI backend loads the active models from this directory at startup to perform inference.
