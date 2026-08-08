import os
import json
import pandas as pd
import numpy as np
import joblib

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Optional LightGBM import
try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

# Metrics
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

def load_processed_data(train_path: str, test_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads preprocessed training and testing datasets."""
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Processed training or testing dataset is missing. Run preprocessing first.")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    return train_df, test_df

def split_features_target(df: pd.DataFrame, target_col: str = "loan_status") -> tuple[pd.DataFrame, pd.Series]:
    """Splits DataFrame into features (X) and target (y)."""
    X = df.drop(columns=[target_col])
    y = df[target_col].astype(int)
    return X, y

def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Calculates all requested classification metrics on the testing set."""
    y_pred = model.predict(X_test)
    # Check if model has predict_proba
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        # Fallback if probability prediction is not supported (e.g. some SVMs, not applicable here)
        y_prob = y_pred
        
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)
    
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm.tolist()  # Convert numpy array to serializable list
    }

def get_feature_importances(model, feature_names: list) -> pd.DataFrame:
    """Extracts and normalizes feature importances or coefficients based on model type."""
    importance_df = pd.DataFrame(index=feature_names)
    
    # 1. Check for tree-based feature importances
    if hasattr(model, "feature_importances_"):
        importance_df["importance"] = model.feature_importances_
    # 2. Check for linear model coefficients
    elif hasattr(model, "coef_"):
        # Use absolute coefficients to signify impact size
        importance_df["importance"] = np.abs(model.coef_[0])
        # Normalize to sum to 1 to align representation with tree models
        total = importance_df["importance"].sum()
        if total > 0:
            importance_df["importance"] = importance_df["importance"] / total
    else:
        importance_df["importance"] = 1.0 / len(feature_names) # Default fallback
        
    importance_df = importance_df.sort_values(by="importance", ascending=False).reset_index()
    importance_df.rename(columns={"index": "feature"}, inplace=True)
    return importance_df

def print_model_comparison(results: dict):
    """Prints a clean tabular comparison of the model metrics."""
    print("\n" + "="*80)
    print(f"{'MODEL METRICS COMPARISON (TESTING SET)':^80}")
    print("="*80)
    
    headers = ["Model Name", "Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"]
    print(f"{headers[0]:<25} | {headers[1]:<8} | {headers[2]:<9} | {headers[3]:<7} | {headers[4]:<8} | {headers[5]:<8}")
    print("-" * 80)
    
    for model_name, metrics in results.items():
        print(
            f"{model_name:<25} | "
            f"{metrics['accuracy']:.4f}  | "
            f"{metrics['precision']:.4f}   | "
            f"{metrics['recall']:.4f} | "
            f"{metrics['f1_score']:.4f}   | "
            f"{metrics['roc_auc']:.4f}"
        )
    print("="*80 + "\n")

def run_training_pipeline(
    train_path: str, 
    test_path: str, 
    models_dir: str
):
    """Orchestrates model training, evaluation, comparison, selection, and serialization."""
    print("Starting machine learning model training pipeline...")
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Load data
    train_df, test_df = load_processed_data(train_path, test_path)
    X_train, y_train = split_features_target(train_df)
    X_test, y_test = split_features_target(test_df)
    feature_names = X_train.columns.tolist()
    
    # Initialize models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss"
        )
    }
    
    # Add LightGBM if installed
    if LIGHTGBM_AVAILABLE:
        print("LightGBM is available. Including in comparative training.")
        models["LightGBM"] = LGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
    else:
        print("LightGBM is not available. Skipping LightGBM.")
        
    # 2. Train and evaluate all models
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        results[name] = metrics
        
    # 3. Print comparison table
    print_model_comparison(results)
    
    # 4. Automatically select the best model based on ROC AUC
    # ROC AUC is optimal for credit underwriting ranking tasks
    best_model_name = max(results, key=lambda k: results[k]["roc_auc"])
    best_model = trained_models[best_model_name]
    best_roc_auc = results[best_model_name]["roc_auc"]
    print(f"--> Selected Best Model: {best_model_name} (ROC AUC: {best_roc_auc:.4f})")
    
    # 5. Save best model binary
    model_save_path = os.path.join(models_dir, "risk_model.pkl")
    joblib.dump(best_model, model_save_path)
    print(f"Saved selected model binary to: {model_save_path}")
    
    # 6. Generate and save feature importances for the best model
    importance_df = get_feature_importances(best_model, feature_names)
    importance_save_path = os.path.join(models_dir, "feature_importance.csv")
    importance_df.to_csv(importance_save_path, index=False)
    print(f"Saved feature importances to: {importance_save_path}")
    
    # 7. Generate and save model_metrics.json
    metrics_report = {
        "selected_model": best_model_name,
        "metrics_summary": results
    }
    metrics_save_path = os.path.join(models_dir, "model_metrics.json")
    with open(metrics_save_path, "w") as f:
        json.dump(metrics_report, f, indent=4)
    print(f"Saved evaluation metrics report to: {metrics_save_path}")
    print("Machine learning training pipeline completed successfully!")

if __name__ == "__main__":
    # Define relative paths assuming script runs from workspace root
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TRAIN_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed_train.csv")
    TEST_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed_test.csv")
    MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
    
    run_training_pipeline(TRAIN_PATH, TEST_PATH, MODELS_DIR)
