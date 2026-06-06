from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date
from database import get_db
from models.models import Attendance, Cadet, User
from routers.deps import require_admin, get_current_user

router = APIRouter()

class AttendanceEntry(BaseModel):
    cadet_id:  int
    status:    str   # "present" / "absent" / "leave"

class AttendanceBulk(BaseModel):
    date:    date
    entries: List[AttendanceEntry]

# ── ADMIN ONLY: Mark attendance ───────────────────────────────────────────────
@router.post("/mark")
def mark_attendance(
    data: AttendanceBulk,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    for entry in data.entries:
        if entry.status not in ("present", "absent", "leave"):
            raise HTTPException(status_code=400, detail=f"Invalid status: {entry.status}")

        existing = db.query(Attendance).filter(
            Attendance.cadet_id == entry.cadet_id,
            Attendance.date     == data.date
        ).first()

        if existing:
            existing.status    = entry.status
            existing.marked_by = current_user.id
        else:
            record = Attendance(
                cadet_id  = entry.cadet_id,
                date      = data.date,
                status    = entry.status,
                marked_by = current_user.id
            )
            db.add(record)
    db.commit()
    return {"message": f"Attendance saved for {data.date}"}

# ── ADMIN ONLY: Get attendance by date ────────────────────────────────────────
@router.get("/date/{att_date}")
def get_attendance_by_date(
    att_date: date,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    records = db.query(Attendance).filter(Attendance.date == att_date).all()
    return [
        {
            "cadet_id": r.cadet_id,
            "date":     str(r.date),
            "status":   r.status
        }
        for r in records
    ]

# ── Any authenticated user: view their OWN attendance ─────────────────────────
@router.get("/my")
def get_my_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cadets can only view their own attendance record."""
    cadet = db.query(Cadet).filter(Cadet.user_id == current_user.id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="No cadet profile found for this user")
    records = db.query(Attendance).filter(Attendance.cadet_id == cadet.id).all()
    total   = len(records)
    present = sum(1 for r in records if r.status == "present")
    return {
        "cadet_id":   cadet.id,
        "total_days": total,
        "present":    present,
        "absent":     total - present,
        "percentage": round(present / total * 100, 1) if total > 0 else 0,
        "records":    [{"date": str(r.date), "status": r.status} for r in records]
    }

# ── ADMIN ONLY: Get attendance for any cadet ──────────────────────────────────
@router.get("/cadet/{cadet_id}")
def get_cadet_attendance(
    cadet_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    records = db.query(Attendance).filter(Attendance.cadet_id == cadet_id).all()
    total   = len(records)
    present = sum(1 for r in records if r.status == "present")
    return {
        "cadet_id":   cadet_id,
        "total_days": total,
        "present":    present,
        "absent":     total - present,
        "percentage": round(present / total * 100, 1) if total > 0 else 0,
        "records":    [{"date": str(r.date), "status": r.status} for r in records]
    }
