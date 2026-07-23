"""
==========================================================================
 ML UTILITIES MODULE
==========================================================================
Loads the trained model + preprocessing objects (created by your
02_train_model.py script) ONCE when the server starts, and provides
functions the API routes can call to get risk scores and recommendations.

This module does NOT retrain anything -- it reuses the exact .pkl files
your existing pipeline already produced.
==========================================================================
"""

import os
import json
import joblib
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --------------------------------------------------------------------
# Load everything ONCE at import time (i.e. when the server starts)
# --------------------------------------------------------------------
model = joblib.load(os.path.join(DATA_DIR, "dropout_model.pkl"))
scaler = joblib.load(os.path.join(DATA_DIR, "scaler.pkl"))
encoders = joblib.load(os.path.join(DATA_DIR, "label_encoders.pkl"))
feature_names = joblib.load(os.path.join(DATA_DIR, "feature_names.pkl"))

students_df = pd.read_csv(os.path.join(DATA_DIR, "student_dropout_dataset.csv"))
risk_df = pd.read_csv(os.path.join(DATA_DIR, "student_risk_scores.csv"))
recs_df = pd.read_csv(os.path.join(DATA_DIR, "counseling_recommendations.csv"))
feature_importance_df = pd.read_csv(os.path.join(DATA_DIR, "feature_importance.csv"))

with open(os.path.join(DATA_DIR, "model_metrics.json")) as f:
    model_metrics = json.load(f)

THRESHOLD = model_metrics.get("tuned_threshold_value", 0.42)

# Merge student features with their precomputed risk score + tier.
# This is the single source of truth the API will read from.
MERGED_DF = students_df.merge(
    risk_df[["student_id", "dropout_probability", "risk_tier"]],
    on="student_id",
    how="left",
)


# --------------------------------------------------------------------
# Helper: convert a pandas row into a clean JSON-serializable dict
# --------------------------------------------------------------------
def row_to_dict(row: pd.Series) -> dict:
    d = row.to_dict()
    # Convert numpy types to native Python types so FastAPI can serialize
    for k, v in d.items():
        if pd.isna(v):
            d[k] = None
        elif hasattr(v, "item"):  # numpy scalar -> python scalar
            d[k] = v.item()
    return d


# --------------------------------------------------------------------
# Public functions used by the API routes
# --------------------------------------------------------------------
def get_all_students(risk_tier: str = None, search: str = None):
    df = MERGED_DF.copy()
    if risk_tier and risk_tier.lower() != "all":
        df = df[df["risk_tier"].str.lower() == risk_tier.lower()]
    if search:
        df = df[df["student_id"].str.contains(search, case=False, na=False)]
    df = df.sort_values("dropout_probability", ascending=False)
    return [row_to_dict(row) for _, row in df.iterrows()]


def get_student_by_id(student_id: str):
    match = MERGED_DF[MERGED_DF["student_id"] == student_id]
    if match.empty:
        return None
    return row_to_dict(match.iloc[0])


def get_recommendations_for_student(student_id: str):
    match = recs_df[recs_df["student_id"] == student_id]
    return match.to_dict(orient="records")


def get_high_risk_students(limit: int = None):
    df = MERGED_DF[MERGED_DF["risk_tier"] == "High Risk"].sort_values(
        "dropout_probability", ascending=False
    )
    if limit:
        df = df.head(limit)
    return [row_to_dict(row) for _, row in df.iterrows()]


def get_overview_stats():
    total = len(MERGED_DF)
    tier_counts = MERGED_DF["risk_tier"].value_counts().to_dict()
    return {
        "total_students": int(total),
        "high_risk_count": int(tier_counts.get("High Risk", 0)),
        "medium_risk_count": int(tier_counts.get("Medium Risk", 0)),
        "low_risk_count": int(tier_counts.get("Low Risk", 0)),
        "avg_dropout_probability": float(round(MERGED_DF["dropout_probability"].mean(), 2)),
    }


def get_feature_importance():
    return feature_importance_df.sort_values(
        "importance", ascending=False
    ).to_dict(orient="records")


def get_model_metrics():
    return model_metrics


def predict_new_student(features: dict) -> dict:
    """
    Takes a dict of raw feature values (matching feature_names) for a
    NEW/hypothetical student not in the dataset, and returns a dropout
    probability + risk tier. Used by an optional 'what-if' calculator
    in the UI, and demonstrates the model works on fresh input, not
    just memorized training data.
    """
    row = {}
    for col in feature_names:
        if col not in features:
            raise ValueError(f"Missing required feature: {col}")
        row[col] = features[col]

    df_input = pd.DataFrame([row])

    # Apply the SAME label encoders used during training. If the frontend
    # sends a category value the encoder has never seen (e.g. a typo),
    # raise a clear, catchable error instead of letting sklearn crash with
    # an unreadable internal exception.
    for col, le in encoders.items():
        valid_values = set(le.classes_)
        if df_input[col].iloc[0] not in valid_values:
            raise ValueError(
                f"Invalid value '{df_input[col].iloc[0]}' for '{col}'. "
                f"Expected one of: {sorted(valid_values)}"
            )
        df_input[col] = le.transform(df_input[col])

    df_input = df_input[feature_names]  # ensure correct column order

    proba = model.predict_proba(df_input)[0, 1]
    proba_pct = float(round(proba * 100, 1))

    if proba_pct >= 55:
        tier = "High Risk"
    elif proba_pct >= 30:
        tier = "Medium Risk"
    else:
        tier = "Low Risk"

    return {"dropout_probability": proba_pct, "risk_tier": tier}
