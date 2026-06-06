from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.models import User, Cadet, Attendance, Event, Announcement
from routers.auth import hash_password
from routers.deps import require_admin

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name:     str
    email:    str
    password: str
    role:     str = "cadet"

class UserUpdate(BaseModel):
    name:     Optional[str] = None
    email:    Optional[str] = None
    password: Optional[str] = None
    role:     Optional[str] = None

# ── Dashboard stats ───────────────────────────────────────────────────────────

@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    return {
        "total_users":      db.query(User).count(),
        "total_cadets":     db.query(Cadet).count(),
        "pending_cadets":   db.query(Cadet).filter(Cadet.approved == False).count(),
        "approved_cadets":  db.query(Cadet).filter(Cadet.approved == True).count(),
        "total_events":     db.query(Event).count(),
        "total_announce":   db.query(Announcement).count(),
        "total_attendance": db.query(Attendance).count(),
        "officers":         db.query(User).filter(User.role == "officer").count(),
        "admins":           db.query(User).filter(User.role == "admin").count(),
    }

# ── User management ───────────────────────────────────────────────────────────

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id":         u.id,
            "name":       u.name,
            "email":      u.email,
            "role":       u.role,
            "created_at": str(u.created_at) if u.created_at else "",
        }
        for u in users
    ]

@router.post("/users")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name     = data.name,
        email    = data.email,
        password = hash_password(data.password),
        role     = data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "id": user.id}

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.name     is not None: user.name     = data.name
    if data.email    is not None: user.email    = data.email
    if data.role     is not None: user.role     = data.role
    if data.password is not None: user.password = hash_password(data.password)
    db.commit()
    return {"message": "User updated"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cadet = db.query(Cadet).filter(Cadet.user_id == user_id).first()
    if cadet:
        db.query(Attendance).filter(Attendance.cadet_id == cadet.id).delete()
        db.delete(cadet)
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

# ── Cadet approval (Admin only) ───────────────────────────────────────────────

@router.post("/cadets/{cadet_id}/approve")
def approve_cadet(
    cadet_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    cadet = db.query(Cadet).filter(Cadet.id == cadet_id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="Cadet not found")
    if cadet.approved:
        raise HTTPException(status_code=400, detail="Cadet is already approved")
    cadet.approved = True
    db.commit()
    return {"message": "Cadet approved successfully"}

@router.post("/cadets/{cadet_id}/reject")
def reject_cadet(
    cadet_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    cadet = db.query(Cadet).filter(Cadet.id == cadet_id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="Cadet not found")
    user_id = cadet.user_id
    db.query(Attendance).filter(Attendance.cadet_id == cadet_id).delete()
    db.delete(cadet)
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return {"message": "Cadet rejected and removed"}
