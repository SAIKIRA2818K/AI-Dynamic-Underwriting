# AI-Driven Dynamic Underwriting System

An AI-powered lending and risk assessment system developed for the **AI Build 2026 Hackathon**. This application uses both traditional financial data (income, credit score, debt levels) and alternative digital footprints (utility and rent payment histories, cash flow transaction patterns) to evaluate loan application risks, identify anomalies/fraud, and generate transparent explanations.

## Tech Stack
- **Frontend**: React (TypeScript) + Vite
- **Backend**: FastAPI (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Machine Learning**: 
  - **XGBoost**: For predicting probability of loan default (risk scoring).
  - **Isolation Forest**: For detecting outliers and transactional anomalies (fraud/risk flag).
- **Explainability**: OpenAI API for generating natural language descriptions of risk factors and loan decisions.

---

## Directory Structure and Purposes

Below is the directory structure generated for the project:

```text
AI_BUILD/
├── .gitignore                      # Root Git ignore configuration
├── README.md                       # Main project documentation (this file)
├── dataset/                        # Data management and generation folder
│   └── README.md                   # Details about dataset usage (raw/processed)
├── models/                         # Serialized ML model binaries & checkpoints
│   └── README.md                   # Guidelines on XGBoost/Isolation Forest serializations
├── utils/                          # ML utility scripts & training pipelines
│   ├── README.md                   # Guidelines on training/preprocessing scripts
│   ├── data_preprocessing.py       # Data cleaning, scaling, and feature engineering
│   └── train_models.py             # Script to train and export XGBoost & Isolation Forest models
├── backend/                        # FastAPI web application (Python)
│   ├── requirements.txt            # Python dependencies
│   └── app/                        # FastAPI core code
│       ├── __init__.py
│       ├── main.py                 # API entrypoint and router configuration
│       ├── api/                    # Route endpoints handling incoming requests
│       │   ├── __init__.py
│       │   └── endpoints/
│       │       ├── __init__.py
│       │       ├── auth.py         # Sign-up and Login authentication routing
│       │       └── underwriting.py # Main underwriting evaluation POST route
│       ├── core/                   # Global configuration and settings
│       │   ├── __init__.py
│       │   └── config.py
│       ├── db/                     # SQLite connection and session management
│       │   ├── __init__.py
│       │   ├── base.py             # Global DB model base
│       │   └── session.py          # Session engines and DB generators
│       ├── schemas/                # Pydantic data schemas validation models
│       │   ├── __init__.py
│       │   ├── auth.py             # Login/registration validation schemas
│       │   └── underwriting.py     # Underwriting request and response formats
│       └── services/               # Core underwriting orchestration & ML inference logic
│           ├── __init__.py
│           └── underwriting.py     # Invokes models & OpenAI prompts (Business logic layer)
└── frontend/                       # React client application (TypeScript + Vite)
    ├── package.json                # NPM packages and configurations
    ├── tsconfig.json               # TypeScript setup
    ├── vite.config.ts              # Vite bundle configurations
    ├── index.html                  # Core HTML file
    ├── public/                     # Static assets
    └── src/                        # Component and view files
```

---

## Folders Breakdown

### 1. `frontend/`
- **Purpose**: Holds the client-side user interface. Built using **React** scaffolded with **Vite** and **TypeScript** for fast development and static type safety.
- **Usage**: Underwriters and administrators will log into this interface to submit loan profiles, monitor real-time risk evaluations, and inspect AI-generated risk decision explanations.

### 2. `backend/`
- **Purpose**: Holds the **FastAPI** web server. Manages routing, databases, API validations, and triggers the machine learning models.
- **Usage**: The backend exposes endpoints for submitting application data, queries SQLite for history records, and coordinates ML models alongside OpenAI explanation generations.

### 3. `models/`
- **Purpose**: Acts as a repository for serialized models (`.json` or `.joblib` files) such as the trained XGBoost model and Isolation Forest detector.
- **Usage**: The FastAPI backend references this directory directly to load saved models into memory at runtime for immediate inference.

### 4. `dataset/`
- **Purpose**: Stores the raw, processed, or synthetically generated loan files.
- **Usage**: Keeps source data localized for local model iterations. Separates raw inputs from engineering features, protecting analytical pipelines.

### 5. `utils/`
- **Purpose**: Stores administrative modules, cleaning procedures, and offline model training steps.
- **Usage**: Contains script files like `train_models.py` which are run periodically or in automated workflows to retrain XGBoost/Isolation Forest models.
