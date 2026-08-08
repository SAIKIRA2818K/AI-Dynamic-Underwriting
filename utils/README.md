# Utilities and Scripts Directory

This directory holds utility scripts, data preprocessing functions, and ML training pipelines.

## Structure
- `train_models.py`: Python script that reads the processed datasets, trains the XGBoost risk model and Isolation Forest model, and outputs serialized objects to `../models/`.
- `data_preprocessing.py`: Modules to clean and transform raw datasets into ML-ready inputs.
- `openai_explainer.py`: Helper script to prototype and test OpenAI prompts for generating risk-decision explanations.
