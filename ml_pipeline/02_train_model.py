"""
==========================================================================
 STEP 2: ML PIPELINE - DROPOUT PREDICTION MODEL
==========================================================================
This script covers:
  1. Load & explore data (EDA)
  2. Preprocess (encode categorical, scale numeric)
  3. Train/test split
  4. Train 2 models: Logistic Regression (baseline) + Random Forest (main)
  5. Evaluate using Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC
  6. Extract feature importance -> answers "WHY do students drop out?"
  7. Generate a dropout PROBABILITY SCORE per student (not just yes/no)
  8. Save the trained model + scaler + encoder for later use in the dashboard
==========================================================================
"""

import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)

import matplotlib
matplotlib.use("Agg")  # so plots save to file instead of needing a display
import matplotlib.pyplot as plt

DATA_PATH = "student_dropout_dataset.csv"
OUT_DIR = "."

# ==========================================================================
# 1. LOAD DATA
# ==========================================================================
df = pd.read_csv(DATA_PATH)
print("Dataset shape:", df.shape)
print("\nColumn types:\n", df.dtypes)
print("\nMissing values per column:\n", df.isnull().sum().sum(), "total missing values")

# ==========================================================================
# 2. PREPROCESSING
# ==========================================================================
# Drop student_id - it's just an identifier, not a predictive feature.
# We keep it aside so we can map predictions back to specific students later
# (needed for the dashboard / alert system).
student_ids = df['student_id']
df_model = df.drop(columns=['student_id'])

# Identify categorical columns that need encoding
categorical_cols = ['gender', 'category', 'hostel_or_dayscholar']

# Label Encoding: converts text categories into numbers (e.g. Male=0, Female=1)
# We save each encoder because the SAME encoding must be used later when a
# new/real student's data is fed into the model.
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    encoders[col] = le

# Separate features (X) and target label (y)
X = df_model.drop(columns=['dropout'])
y = df_model['dropout']

feature_names = X.columns.tolist()
print("\nFeatures used for prediction:\n", feature_names)

# ==========================================================================
# 3. TRAIN / TEST SPLIT
# ==========================================================================
# stratify=y ensures both train and test sets keep the same dropout ratio
# (important since our dataset is imbalanced: ~20% dropout, ~80% not)
X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, student_ids, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]}  |  Test set size: {X_test.shape[0]}")

# Scaling: puts all numeric features on a similar scale (0 mean, 1 std dev).
# Logistic Regression NEEDS this to work well. Random Forest doesn't need it,
# but it doesn't hurt, so we apply it consistently.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================================================
# 4. TRAIN MODELS
# ==========================================================================

# --- Model 1: Logistic Regression (simple baseline) ---
# Good to include in your report as a "baseline" to show improvement.
log_reg = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
log_reg.fit(X_train_scaled, y_train)

# --- Model 2: Random Forest (main model) ---
# class_weight='balanced' tells the model to pay MORE attention to the
# minority class (dropouts), since they're rarer in the data. Without this,
# the model could get "lazy" and just predict "not dropout" for everyone
# and still get ~80% accuracy -- which would be useless in practice!
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)
rf_model.fit(X_train, y_train)  # Random Forest can use unscaled data directly

# ==========================================================================
# 5. EVALUATE BOTH MODELS
# ==========================================================================
def evaluate_model(name, y_true, y_pred, y_proba):
    print(f"\n--- {name} ---")
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)
    print(f"Accuracy : {acc:.3f}")
    print(f"Precision: {prec:.3f}  (of predicted dropouts, how many were correct)")
    print(f"Recall   : {rec:.3f}  (of actual dropouts, how many we caught)")
    print(f"F1-score : {f1:.3f}")
    print(f"ROC-AUC  : {auc:.3f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=['Not Dropout', 'Dropout']))
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1, 'auc': auc}

log_reg_pred = log_reg.predict(X_test_scaled)
log_reg_proba = log_reg.predict_proba(X_test_scaled)[:, 1]
log_reg_metrics = evaluate_model("Logistic Regression (Baseline)", y_test, log_reg_pred, log_reg_proba)

rf_pred = rf_model.predict(X_test)
rf_proba = rf_model.predict_proba(X_test)[:, 1]
rf_metrics = evaluate_model("Random Forest (Main Model, default threshold=0.5)", y_test, rf_pred, rf_proba)

# --------------------------------------------------------------------
# Threshold tuning: WHY?
# By default, sklearn predicts "Dropout" only if probability > 0.5.
# But in a real counseling system, missing an at-risk student (a "false
# negative") is much more costly than wrongly flagging a safe student for
# counseling (a "false positive") -- the worst case of the latter is just
# an unnecessary conversation with a counselor. So we lower the threshold
# to catch MORE at-risk students, accepting more false alarms in exchange.
# This is a real, defensible design decision worth mentioning in your report.
# --------------------------------------------------------------------
THRESHOLD = 0.42
rf_pred_tuned = (rf_proba >= THRESHOLD).astype(int)
rf_metrics_tuned = evaluate_model(
    f"Random Forest (Tuned threshold={THRESHOLD})", y_test, rf_pred_tuned, rf_proba
)

# ==========================================================================
# 6. FEATURE IMPORTANCE -> "Why do students drop out?" (Objective 2)
# ==========================================================================
importances = pd.DataFrame({
    'feature': feature_names,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n--- Top factors contributing to dropout (Feature Importance) ---")
print(importances.head(10).to_string(index=False))

importances.to_csv(f"{OUT_DIR}/feature_importance.csv", index=False)

# Plot feature importance
plt.figure(figsize=(8, 6))
top_features = importances.head(10)
plt.barh(top_features['feature'], top_features['importance'], color='#4C72B0')
plt.xlabel("Importance Score")
plt.title("Top 10 Factors Contributing to Student Dropout")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/feature_importance.png", dpi=150)
plt.close()
print(f"\nFeature importance chart saved to {OUT_DIR}/feature_importance.png")

# ==========================================================================
# 7. CONFUSION MATRIX PLOT (good for your report/presentation)
# ==========================================================================
cm = confusion_matrix(y_test, rf_pred_tuned)
plt.figure(figsize=(5, 4))
plt.imshow(cm, cmap='Blues')
plt.title(f"Confusion Matrix - Random Forest (threshold={THRESHOLD})")
plt.colorbar()
plt.xticks([0, 1], ['Not Dropout', 'Dropout'])
plt.yticks([0, 1], ['Not Dropout', 'Dropout'])
plt.xlabel("Predicted")
plt.ylabel("Actual")
for i in range(2):
    for j in range(2):
        plt.text(j, i, str(cm[i, j]), ha='center', va='center',
                  color='white' if cm[i, j] > cm.max()/2 else 'black', fontsize=14)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/confusion_matrix.png", dpi=150)
plt.close()

# ==========================================================================
# 8. ROC CURVE PLOT
# ==========================================================================
fpr, tpr, _ = roc_curve(y_test, rf_proba)
plt.figure(figsize=(5, 5))
plt.plot(fpr, tpr, label=f"Random Forest (AUC = {rf_metrics['auc']:.3f})", color='#C44E52')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label="Random guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Dropout Prediction")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/roc_curve.png", dpi=150)
plt.close()

# ==========================================================================
# 9. GENERATE DROPOUT PROBABILITY SCORE PER STUDENT (key feature!)
# ==========================================================================
# This produces a per-student risk score (0-100%) plus a risk tier label.
# This is exactly the "Dropout probability score" feature in your spec,
# and feeds directly into the "Risk Prediction Dashboard" and
# "Admin/teacher alert system" features.

all_proba = rf_model.predict_proba(X)[:, 1]  # probability for ALL students

results = pd.DataFrame({
    'student_id': student_ids,
    'dropout_probability': (all_proba * 100).round(1),
    'actual_dropout': y.values
})

def risk_tier(p):
    if p >= 55:
        return 'High Risk'
    elif p >= 30:
        return 'Medium Risk'
    else:
        return 'Low Risk'

results['risk_tier'] = results['dropout_probability'].apply(risk_tier)
results = results.sort_values('dropout_probability', ascending=False)
results.to_csv(f"{OUT_DIR}/student_risk_scores.csv", index=False)

print("\n--- Sample of student risk scores (top 10 highest risk) ---")
print(results.head(10).to_string(index=False))

print("\nRisk tier distribution:")
print(results['risk_tier'].value_counts())

# ==========================================================================
# 10. SAVE MODEL + PREPROCESSING OBJECTS (for dashboard / API use later)
# ==========================================================================
joblib.dump(rf_model, f"{OUT_DIR}/dropout_model.pkl")
joblib.dump(scaler, f"{OUT_DIR}/scaler.pkl")
joblib.dump(encoders, f"{OUT_DIR}/label_encoders.pkl")
joblib.dump(feature_names, f"{OUT_DIR}/feature_names.pkl")

# Save metrics summary as JSON (useful for your report appendix)
metrics_summary = {
    'logistic_regression': log_reg_metrics,
    'random_forest_default_threshold': rf_metrics,
    'random_forest_tuned_threshold': rf_metrics_tuned,
    'tuned_threshold_value': THRESHOLD,
    'dataset_size': len(df),
    'dropout_rate_pct': round(y.mean() * 100, 2),
    'features_used': feature_names
}
with open(f"{OUT_DIR}/model_metrics.json", "w") as f:
    json.dump(metrics_summary, f, indent=2)

print("\n=== Model, scaler, encoders, and metrics saved successfully ===")
print(f"All output files are in: {OUT_DIR}")
