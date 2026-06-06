from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.models import User, Cadet

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY          = "ncc_secret_key_change_in_production"
ALGORITHM           = "HS256"
TOKEN_EXPIRE_HOURS  = 24

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str
    email:    str
    password: str
    roll_no:  str = ""
    unit:     str = "Alpha Company"
    # role is NOT accepted from user input — always forced to "cadet"

class LoginRequest(BaseModel):
    email:    str
    password: str

# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def validate_password_strength(password: str):
    """Enforce: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char."""
    import re
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\\|,.<>\/?`~]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character (!@#$%^&* etc.).")

def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub":  str(user_id),
        "role": role,
        "exp":  datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 🔒 Public registration ALWAYS creates a cadet — never admin/officer
    forced_role = "cadet"

    validate_password_strength(data.password)

    user = User(
        name     = data.name,
        email    = data.email,
        password = hash_password(data.password),
        role     = forced_role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if data.roll_no:
        cadet = Cadet(
            user_id  = user.id,
            roll_no  = data.roll_no,
            unit     = data.unit,
            approved = False
        )
        db.add(cadet)
        db.commit()

    return {"message": "Registered successfully! Your account is pending admin approval."}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id, user.role)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user.role,
        "name":         user.name,
        "user_id":      user.id
    }


@router.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    """
    One-time endpoint to create the default admin account.
    Run once after first deploy, then disable this endpoint.
    Default credentials: admin@ncc.com / Ncc@Admin#2025
    """
    existing = db.query(User).filter(User.email == "admin@ncc.com").first()
    if existing:
        return {"message": "Admin account already exists."}

    admin = User(
        name     = "System Admin",
        email    = "admin@ncc.com",
        password = hash_password("Ncc@Admin#2025"),
        role     = "admin"
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin account created. Email: admin@ncc.com | Password: Ncc@Admin#2025"}


# ── Change Password ───────────────────────────────────────────────────────────

from fastapi import Header
from typing import Optional

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

def get_current_user_from_token(token: str, db: Session):
    from jose import JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    user  = get_current_user_from_token(token, db)

    if not verify_password(data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    validate_password_strength(data.new_password)

    user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
