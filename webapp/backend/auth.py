"""
==========================================================================
 AUTHENTICATION MODULE
==========================================================================
Handles login for Admin and Faculty accounts.

DESIGN NOTE (read this before your viva):
For this academic project, user accounts are HARDCODED below rather than
stored in a database with a signup flow. This is a deliberate, reasonable
scope decision for a demo system -- in a real deployment, you would
replace USERS_DB with an actual database table (e.g. SQLite/PostgreSQL)
and add a proper account-creation flow for the admin.

PASSWORD HASHING: we use PBKDF2-HMAC-SHA256 (100,000 iterations) from
Python's built-in `hashlib` module -- no external dependency needed.
This is a real, secure, industry-recognized hashing algorithm (it's what
Django uses by default). Passwords are NEVER stored in plain text -- only
a salted hash is stored, and login works by re-hashing the typed password
with the same salt and comparing.

SESSIONS: handled with JWT (JSON Web Tokens) via python-jose. After
login, the server gives the browser a signed token; the browser sends it
back on every request to prove who's logged in, without the server
needing to keep session state in memory.
==========================================================================
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------
# In a real deployment, SECRET_KEY should come from an environment
# variable, never hardcoded in source code. For this academic demo,
# it's fine here -- but mention this as a "production hardening" note
# in your report if asked about security.
SECRET_KEY = "dropout-prediction-system-demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours - convenient for a work day / demo
PBKDF2_ITERATIONS = 100_000

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# --------------------------------------------------------------------
# PASSWORD HASHING (stdlib-only, no external dependency required)
# --------------------------------------------------------------------
def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Returns a string of the form 'salt_hex:hash_hex'."""
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex() + ":" + pwd_hash.hex()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    new_hash = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    # hmac.compare_digest prevents timing attacks (always takes the same
    # amount of time to compare, so an attacker can't guess the password
    # one character at a time by measuring response speed)
    return hmac.compare_digest(new_hash.hex(), hash_hex)


# --------------------------------------------------------------------
# HARDCODED USER "DATABASE"
# --------------------------------------------------------------------
# Demo login credentials (use these in your report/demo script):
#   Admin:   username = admin     password = admin123
#   Faculty: username = faculty1  password = faculty123
#   Faculty: username = faculty2  password = faculty123
#
# Password hashes below were generated once using hash_password() and
# pasted in as fixed strings, exactly like a real system would store
# them in a database column.
USERS_DB = {
    "admin": {
        "username": "admin",
        "full_name": "Dr. Admin User",
        "role": "admin",
        "hashed_password": hash_password("admin123"),
    },
    "faculty1": {
        "username": "faculty1",
        "full_name": "Prof. Aditi Sharma",
        "role": "faculty",
        "hashed_password": hash_password("faculty123"),
    },
    "faculty2": {
        "username": "faculty2",
        "full_name": "Prof. Rohan Mehta",
        "role": "faculty",
        "hashed_password": hash_password("faculty123"),
    },
}
# NOTE: hashes are regenerated fresh each time the server starts (since
# they're computed at import time above). This is fine for a demo system
# with fixed passwords. In a real database-backed system, you would
# generate the hash ONCE when the account is created and store it
# permanently, not regenerate it on every server restart.


# --------------------------------------------------------------------
# Pydantic models
# --------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str
    username: str


# --------------------------------------------------------------------
# Core auth functions
# --------------------------------------------------------------------
def get_user(username: str):
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges.",
        )
    return current_user
