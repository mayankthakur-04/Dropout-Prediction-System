# AI-Based Dropout Prediction and Counseling System

A machine learning system that predicts student dropout risk in Indian colleges and generates personalized counseling recommendations — delivered as a full-stack web application with role-based access for faculty and administrators.

> Built as a Minor Project for B.Tech CSE (Data Science), Oriental College of Technology, Bhopal (RGPV-affiliated).

---

## What it does

Most colleges identify at-risk students only after the damage is done — failed semesters, mounting fee dues, disengagement. This system flags students *before* that point, using data already available in every college's administrative systems: attendance registers, exam records, fee office, LMS logs, and admission forms.

For each flagged student, it doesn't just assign a risk score — it explains *why* the student is at risk and *what a counselor should do about it*, mapped to the specific factors driving that student's risk (low attendance, fee overdue, weak academics, etc.).

---

## Features

| Feature | Description |
|---|---|
| **Risk Prediction Dashboard** | Searchable, filterable table of all students with dropout probability scores and risk tiers |
| **Early Warning Alerts** | Expandable list of High Risk students with counseling recommendations, ready for faculty action |
| **Student Drill-Down** | Full profile + personalized counseling plan for any individual student |
| **Risk Calculator** | Live what-if predictor — enter any student's details and get an instant model prediction |
| **Model Insights** | Feature importance chart, confusion matrix, ROC-AUC, and model comparison metrics |
| **Role-Based Access** | Separate faculty and admin roles; admin additionally manages user accounts |
| **Secure Login** | JWT sessions, PBKDF2-HMAC-SHA256 password hashing |

---

## Project structure

```
Dropout_Prediction_Project/
│
├── 01_generate_dataset.py       # Generates synthetic Indian college student dataset
├── 02_train_model.py            # Trains ML models, evaluates, saves .pkl artifacts
├── 03_counseling_engine.py      # Rule-based counseling recommendation generator
├── 04_dashboard.py              # Streamlit prototype dashboard (local, quick demo)
│
├── student_dropout_dataset.csv  # 2,000-student synthetic dataset (19 features)
├── student_risk_scores.csv      # Per-student dropout probability + risk tier
├── counseling_recommendations.csv  # Counseling action report for flagged students
├── model_metrics.json           # Accuracy, precision, recall, F1, AUC for both models
│
├── dropout_model.pkl            # Trained Random Forest classifier
├── scaler.pkl                   # StandardScaler (same used in training)
├── label_encoders.pkl           # LabelEncoders for categorical features
├── feature_names.pkl            # Ordered feature list for consistent input format
│
├── feature_importance.png       # Top 10 dropout factors (bar chart)
├── confusion_matrix.png         # Confusion matrix at tuned threshold (0.42)
├── roc_curve.png                # ROC curve with AUC annotation
│
└── dropout_webapp/
    ├── backend/
    │   ├── main.py              # FastAPI app — all 9 REST endpoints
    │   ├── auth.py              # Login, JWT, hardcoded demo accounts
    │   ├── ml_utils.py          # Loads model, serves predictions and recommendations
    │   ├── requirements.txt
    │   └── data/                # Copies of CSVs + .pkl files for the backend to load
    └── frontend/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        └── src/
            ├── api/client.js        # All backend API calls, JWT handling
            ├── context/AuthContext.jsx
            ├── components/          # DashboardLayout, RiskBadge, Card, StatCard
            └── pages/               # Login, Overview, Students, Detail, Alerts,
                                     # Calculator, ModelInsights, AdminUsers
```

---

## Tech stack

**ML pipeline**
- Python 3.10+ (Anaconda)
- scikit-learn — Random Forest, Logistic Regression, StandardScaler, LabelEncoder
- pandas, numpy — data generation and preprocessing
- matplotlib — evaluation charts
- joblib — model serialization

**Backend**
- FastAPI — REST API with automatic `/docs` OpenAPI interface
- uvicorn — ASGI server
- python-jose — JWT token generation and verification
- PBKDF2-HMAC-SHA256 (Python stdlib) — password hashing, no external dependency

**Frontend**
- React 18 + Vite
- react-router-dom — client-side routing
- Recharts — pie chart and bar charts
- CSS custom properties (design tokens) — no UI framework dependency

---

## Getting started

### Prerequisites

- Python (Anaconda recommended) — for the ML pipeline and backend
- Node.js v18+ — for the frontend

### Step 1 — Run the ML pipeline

```bash
# Run from the project root (not the webapp folder)
python 01_generate_dataset.py
python 02_train_model.py
python 03_counseling_engine.py
```

Each script depends on the previous one's output. After this, you'll have the dataset CSVs, trained model `.pkl` files, and evaluation charts.

### Step 2 — Start the backend

```bash
cd dropout_webapp/backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Verify it's running: open `http://localhost:8000/docs` — you should see the interactive API docs.

> **Windows users:** if `python` or `uvicorn` isn't recognized, use the full Anaconda path:
> ```
> & "C:\Users\<YourName>\anaconda3\python.exe" -m uvicorn main:app --reload --port 8000
> ```

### Step 3 — Start the frontend

Open a **second terminal** (keep the backend running in the first):

```bash
cd dropout_webapp/frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Faculty | `faculty1` | `faculty123` |
| Faculty | `faculty2` | `faculty123` |

---

## Model details

The dataset is **synthetic** — generated to mirror real Indian college administrative data (attendance registers, exam cell records, fee office, LMS, admission forms). Real student data was not used due to privacy constraints; this is clearly disclosed in the system.

| Metric | Logistic Regression | Random Forest (default) | Random Forest (tuned, threshold=0.42) |
|---|---|---|---|
| Accuracy | 73.2% | 77.2% | 66.2% |
| Precision | 35.9% | 41.6% | 31.6% |
| Recall | 38.5% | 41.0% | **62.8%** |
| F1-Score | 37.1% | 41.3% | **42.1%** |
| ROC-AUC | 61.5% | 69.4% | **69.4%** |

The threshold was tuned from 0.5 to 0.42 deliberately: in a counseling system, missing an at-risk student (false negative) is more harmful than scheduling an unnecessary counseling session (false positive). Higher recall at the cost of some accuracy is the right trade-off here.

**Top dropout predictors (feature importance):**
1. Attendance percentage
2. Assignment submission rate
3. Family income (monthly)
4. Internal marks average
5. Distance from college
6. CGPA
7. Fee delay days

---

## Dataset features

| Category | Features |
|---|---|
| Academic | `attendance_pct`, `internal_marks_avg`, `prev_semester_pct`, `cgpa`, `backlogs` |
| Engagement | `assignment_submission_rate`, `lms_login_freq_per_week`, `library_visits_per_month`, `extracurricular_participation` |
| Financial | `family_income_monthly`, `fee_due`, `fee_delay_days`, `scholarship_status` |
| Demographic | `gender`, `category` (General/OBC/SC/ST/EWS), `hostel_or_dayscholar`, `first_generation_learner`, `distance_from_college_km` |

---

## Known limitations

- **Synthetic data only.** The model has never seen real student records. Accuracy on real data may differ; retraining with institutional data is the recommended next step.
- **sklearn version sensitivity.** The `.pkl` files must be loaded with a scikit-learn version close to the one used to train them. If you see `InconsistentVersionWarning`, retrain the model in your environment by re-running `02_train_model.py`.
- **Local deployment only.** Both servers run locally. No internet access is needed to use the system, but it's not accessible from other devices without additional configuration.
- **Progress monitoring is simulated.** The Streamlit dashboard's progress tracking is illustrative — real longitudinal tracking requires semester-by-semester re-scoring with updated data.

---

## Roadmap

- [ ] Retrain model on real anonymized college data
- [ ] Cloud deployment (Render backend + Vercel frontend)
- [ ] Email/SMS alerts when a student crosses the High Risk threshold
- [ ] Direct LMS integration (Moodle/Fedena API) for automatic data ingestion
- [ ] Semester-by-semester progress tracking with actual re-scoring
- [ ] XGBoost / LightGBM model comparison
- [ ] Multi-institution support

---

## Project info
![Mayank Thakur](https://img.shields.io/badge/Author-Mayank%20Thakur-purple)

![Institution](https://img.shields.io/badge/Institution-Oriental%20College%20of%20Technology-blue)
![Program](https://img.shields.io/badge/Program-B.Tech%20CSE%20(Data%20Science)-green)
![Type](https://img.shields.io/badge/Project-Minor%20Project-orange)
![Year](https://img.shields.io/badge/Year-2025--26-lightgrey)
