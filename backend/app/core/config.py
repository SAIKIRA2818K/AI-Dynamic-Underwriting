import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI-Driven Dynamic Underwriting System"
    
    # SQLite Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./underwriting.db")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ML Model Paths
    XGBOOST_MODEL_PATH: str = os.getenv("XGBOOST_MODEL_PATH", "../models/xgboost_risk_model.json")
    ISOLATION_FOREST_PATH: str = os.getenv("ISOLATION_FOREST_PATH", "../models/anomaly_detector.joblib")
    
    class Config:
        case_sensitive = True

settings = Settings()
