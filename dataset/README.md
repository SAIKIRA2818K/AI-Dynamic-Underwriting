# Dataset Directory

This directory stores datasets used for training and evaluating the underwriting models.

## Structure
- `raw/`: Raw, un-preprocessed loan application data, credit bureau logs, and alternative transaction histories.
- `processed/`: Cleansed, normalized, and engineered features ready for XGBoost and Isolation Forest training.
- `synthetic_generator.py`: Script to generate synthetic credit and alternative digital footprint data for development and testing.

## Security Warning
Do not commit actual customer Personally Identifiable Information (PII) or credit histories to this folder. Use synthetic or anonymized data for hackathon presentations.
