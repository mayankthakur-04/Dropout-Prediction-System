"""
==========================================================================
 MAIN FASTAPI APPLICATION
==========================================================================
This is the entry point for the backend server. It exposes REST API
endpoints that the React frontend calls to log in and fetch dashboard
data.

HOW TO RUN:
    1. cd into this 'backend' folder
    2. pip install -r requirements.txt
    3. uvicorn main:app --reload --port 8000

Once running, visit http://localhost:8000/docs to see interactive API
documentation (FastAPI generates this automatically) -- useful for
testing endpoints manually before connecting the frontend, and also
genuinely impressive to show in a viva.
==========================================================================
"""

from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

import auth
import ml_utils

app = FastAPI(
    title="AI-Based Dropout Prediction and Counseling System API",
    description="Backend API serving risk predictions, alerts, and "
                 "counseling recommendations for Indian college students.",
    version="1.0.0",
)

# --------------------------------------------------------------------
# CORS: allows the React frontend (running on a different port/domain)
# to call this API from the browser. In production, replace "*" with
# your actual frontend domain for better security.
# --------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------
# Request/response models
# --------------------------------------------------------------------
class PredictionInput(BaseModel):
    attendance_pct: float
    internal_marks_avg: float
    prev_semester_pct: float
    cgpa: float
    backlogs: int
    assignment_submission_rate: float
    lms_login_freq_per_week: int
    library_visits_per_month: int
    extracurricular_participation: int
    family_income_monthly: float
    first_generation_learner: int
    distance_from_college_km: float
    scholarship_status: int
    fee_due: int
    fee_delay_days: int
    gender: str
    category: str
    hostel_or_dayscholar: str


# ==========================================================================
# AUTH ROUTES
# ==========================================================================
@app.post("/auth/login", response_model=auth.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint. Expects form data (not JSON) with 'username' and
    'password' fields -- this is the standard OAuth2 password flow that
    FastAPI's docs UI and most frontend HTTP libraries expect.
    """
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "full_name": user["full_name"],
        "username": user["username"],
    }


@app.get("/auth/me")
async def read_current_user(current_user: dict = Depends(auth.get_current_user)):
    """Returns info about the currently logged-in user (for the frontend
    to show 'Welcome, Prof. X' and decide whether to show admin features)."""
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
    }


# ==========================================================================
# DASHBOARD DATA ROUTES (all require login)
# ==========================================================================
@app.get("/api/overview")
async def overview(current_user: dict = Depends(auth.get_current_user)):
    return ml_utils.get_overview_stats()


@app.get("/api/students")
async def list_students(
    risk_tier: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(auth.get_current_user),
):
    """List all students, optionally filtered by risk_tier ('High Risk',
    'Medium Risk', 'Low Risk') and/or a student_id search string."""
    return ml_utils.get_all_students(risk_tier=risk_tier, search=search)


@app.get("/api/students/{student_id}")
async def get_student(
    student_id: str, current_user: dict = Depends(auth.get_current_user)
):
    student = ml_utils.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")
    return student


@app.get("/api/students/{student_id}/recommendations")
async def get_student_recommendations(
    student_id: str, current_user: dict = Depends(auth.get_current_user)
):
    student = ml_utils.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")
    return ml_utils.get_recommendations_for_student(student_id)


@app.get("/api/alerts")
async def get_alerts(
    limit: Optional[int] = 50,
    current_user: dict = Depends(auth.get_current_user),
):
    """Returns high-risk students for the Teacher/Admin alerts page."""
    return ml_utils.get_high_risk_students(limit=limit)


@app.get("/api/feature-importance")
async def feature_importance(current_user: dict = Depends(auth.get_current_user)):
    return ml_utils.get_feature_importance()


@app.get("/api/model-metrics")
async def model_metrics(current_user: dict = Depends(auth.get_current_user)):
    return ml_utils.get_model_metrics()


@app.post("/api/predict")
async def predict(
    input_data: PredictionInput,
    current_user: dict = Depends(auth.get_current_user),
):
    """
    'What-if' calculator: lets faculty enter a hypothetical student's
    details and see what risk score the model would assign, without
    that student needing to already exist in the dataset.
    """
    try:
        result = ml_utils.predict_new_student(input_data.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================================================
# ADMIN-ONLY ROUTES
# ==========================================================================
@app.get("/api/admin/users")
async def list_users(current_user: dict = Depends(auth.require_admin)):
    """Admin-only: list all faculty/admin accounts (demo user management)."""
    return [
        {"username": u["username"], "full_name": u["full_name"], "role": u["role"]}
        for u in auth.USERS_DB.values()
    ]


# ==========================================================================
# HEALTH CHECK (useful to confirm the server is up before debugging
# frontend connection issues)
# ==========================================================================
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Dropout Prediction API is running.",
        "docs": "/docs",
    }
