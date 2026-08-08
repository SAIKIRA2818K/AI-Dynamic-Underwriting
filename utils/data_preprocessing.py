import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

def load_data(file_path: str) -> pd.DataFrame:
    """Loads the raw credit risk dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")
    return pd.read_csv(file_path)

def clean_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters out invalid row entries (data entry errors):
    - Age must be <= 100
    - Employment length must be <= 60
    Note: missing values (NaNs) are preserved for later imputation.
    """
    initial_shape = df.shape
    
    # Keep rows where age is <= 100 or is missing
    df = df[(df["person_age"] <= 100) | (df["person_age"].isna())]
    
    # Keep rows where employment length is <= 60 or is missing
    df = df[(df["person_emp_length"] <= 60) | (df["person_emp_length"].isna())]
    
    removed = initial_shape[0] - df.shape[0]
    print(f"Cleaned invalid rows: removed {removed} records.")
    return df

def split_data(df: pd.DataFrame, target_col: str = "loan_status", test_size: float = 0.2, random_state: int = 42):
    """Splits the dataset into train and test sets to prevent data leakage."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Reassemble df for fit-transform steps
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    return train_df, test_df

def fit_preprocessor(train_df: pd.DataFrame, num_cols: list, cat_cols: list):
    """
    Fits preprocessing components (imputers, encoders, scalers) on the training set.
    Saves fit parameters so they can be applied identically to the test set and API inputs.
    """
    print("Fitting preprocessing pipeline on training set...")
    
    # 1. Medians for Imputation
    medians = {
        "person_emp_length": train_df["person_emp_length"].median(),
        "loan_int_rate": train_df["loan_int_rate"].median()
    }
    print(f"Computed training medians for imputation: {medians}")
    
    # Temporarily apply imputation to fit encoders and scalers
    temp_df = train_df.copy()
    for col, val in medians.items():
        temp_df[col] = temp_df[col].fillna(val)
        
    # 2. Ordinal and Binary Manual Encodings
    # Map cb_person_default_on_file (Y/N) -> (1/0)
    # Map loan_grade (A-G) -> (0-6)
    
    # 3. Fit OneHotEncoder for nominal variables
    ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    ohe.fit(temp_df[cat_cols])
    
    # Get column names after OHE
    ohe_feature_names = ohe.get_feature_names_out(cat_cols).tolist()
    
    # Apply manual encoding and OHE to prepare data for Scaler fit
    processed_num_features = []
    
    # Add mapped grades, binary default, and numerical features
    temp_numeric = pd.DataFrame(index=temp_df.index)
    for col in num_cols:
        temp_numeric[col] = temp_df[col]
        
    temp_numeric["loan_grade_encoded"] = temp_df["loan_grade"].map(
        {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
    )
    temp_numeric["cb_person_default_on_file_encoded"] = temp_df["cb_person_default_on_file"].map(
        {"Y": 1, "N": 0}
    )
    
    # Combine standard numerical fields with one-hot encoded columns
    ohe_df = pd.DataFrame(ohe.transform(temp_df[cat_cols]), columns=ohe_feature_names, index=temp_df.index)
    full_numeric_df = pd.concat([temp_numeric, ohe_df], axis=1)
    
    # 4. Fit StandardScaler
    scaler = StandardScaler()
    scaler.fit(full_numeric_df)
    
    preprocessor = {
        "medians": medians,
        "ohe": ohe,
        "scaler": scaler,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "ohe_feature_names": ohe_feature_names,
        "feature_names_out": full_numeric_df.columns.tolist()
    }
    
    return preprocessor

def transform_data(df: pd.DataFrame, preprocessor: dict, target_col: str = "loan_status") -> pd.DataFrame:
    """Transforms raw DataFrame using the fitted preprocessor."""
    transformed_df = df.copy()
    
    # 1. Imputation
    for col, val in preprocessor["medians"].items():
        transformed_df[col] = transformed_df[col].fillna(val)
        
    # 2. Manual Ordinal & Binary Mappings
    transformed_df["loan_grade_encoded"] = transformed_df["loan_grade"].map(
        {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
    ).fillna(-1)  # Fallback if unknown
    
    transformed_df["cb_person_default_on_file_encoded"] = transformed_df["cb_person_default_on_file"].map(
        {"Y": 1, "N": 0}
    ).fillna(0)  # Fallback if unknown
    
    # 3. One Hot Encoding
    ohe_data = preprocessor["ohe"].transform(transformed_df[preprocessor["cat_cols"]])
    ohe_df = pd.DataFrame(
        ohe_data, 
        columns=preprocessor["ohe_feature_names"], 
        index=transformed_df.index
    )
    
    # Assemble feature set for scaling
    numerical_features = pd.DataFrame(index=transformed_df.index)
    for col in preprocessor["num_cols"]:
        numerical_features[col] = transformed_df[col]
    numerical_features["loan_grade_encoded"] = transformed_df["loan_grade_encoded"]
    numerical_features["cb_person_default_on_file_encoded"] = transformed_df["cb_person_default_on_file_encoded"]
    
    features_to_scale = pd.concat([numerical_features, ohe_df], axis=1)
    
    # 4. Scale
    scaled_data = preprocessor["scaler"].transform(features_to_scale)
    
    # Reconstruct final DataFrame
    final_df = pd.DataFrame(
        scaled_data, 
        columns=preprocessor["feature_names_out"], 
        index=transformed_df.index
    )
    
    # Append the target variable back if it exists in the input
    if target_col in df.columns:
        final_df[target_col] = df[target_col].astype(int)
        
    return final_df

def run_preprocessing_pipeline(
    raw_data_path: str, 
    output_dir: str, 
    models_dir: str
):
    """Orchestrates the entire preprocessing workflow."""
    print("Starting preprocessing pipeline...")
    
    # Ensure folders exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Load Data
    raw_df = load_data(raw_data_path)
    print(f"Loaded raw data: {raw_df.shape[0]} rows, {raw_df.shape[1]} columns.")
    
    # 2. Row Filtering
    cleaned_df = clean_invalid_rows(raw_df)
    
    # 3. Split data before fit to prevent leakage
    train_raw, test_raw = split_data(cleaned_df, target_col="loan_status", test_size=0.2, random_state=42)
    print(f"Splits generated: Train={train_raw.shape[0]}, Test={test_raw.shape[0]}")
    
    # Columns definitions
    # Numerical variables to scale
    numerical_columns = [
        "person_age",
        "person_income",
        "person_emp_length",
        "loan_amnt",
        "loan_int_rate",
        "loan_percent_income",
        "cb_person_cred_hist_length"
    ]
    # Nominal categorical variables to OneHotEncode
    categorical_columns = ["person_home_ownership", "loan_intent"]
    
    # 4. Fit pipeline on train set only
    preprocessor = fit_preprocessor(train_raw, numerical_columns, categorical_columns)
    
    # 5. Transform both sets
    processed_train = transform_data(train_raw, preprocessor, target_col="loan_status")
    processed_test = transform_data(test_raw, preprocessor, target_col="loan_status")
    
    # 6. Save outputs
    train_save_path = os.path.join(output_dir, "processed_train.csv")
    test_save_path = os.path.join(output_dir, "processed_test.csv")
    preprocessor_save_path = os.path.join(models_dir, "preprocessor.joblib")
    
    processed_train.to_csv(train_save_path, index=False)
    processed_test.to_csv(test_save_path, index=False)
    joblib.dump(preprocessor, preprocessor_save_path)
    
    print(f"Processed training set saved to: {train_save_path}")
    print(f"Processed testing set saved to: {test_save_path}")
    print(f"Fitted preprocessor saved to: {preprocessor_save_path}")
    print("Preprocessing pipeline completed successfully!")

if __name__ == "__main__":
    # Define relative paths assuming script runs from workspace root
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_PATH = os.path.join(PROJECT_ROOT, "dataset", "credit_risk_dataset.csv")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dataset")
    MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
    
    run_preprocessing_pipeline(RAW_PATH, OUTPUT_DIR, MODELS_DIR)
