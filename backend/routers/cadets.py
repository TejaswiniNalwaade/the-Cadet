from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.models import Cadet, User, Attendance
from backend.routers.deps import get_current_user, require_admin, require_admin_or_officer

router = APIRouter()


class CadetUpdate(BaseModel):
    rank:     Optional[str]  = None
    unit:     Optional[str]  = None
    approved: Optional[bool] = None   # Only admin may change this field


@router.get("/")
def get_all_cadets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Any authenticated user can view the cadet roster."""
    cadets = db.query(Cadet).join(User).all()
    result = []
    for c in cadets:
        total   = db.query(Attendance).filter(Attendance.cadet_id == c.id).count()
        present = db.query(Attendance).filter(Attendance.cadet_id == c.id, Attendance.status == "present").count()
        att_pct = round((present / total * 100), 1) if total > 0 else 0
        result.append({
            "id":         c.id,
            "roll_no":    c.roll_no,
            "name":       c.user.name,
            "email":      c.user.email,
            "rank":       c.rank,
            "unit":       c.unit,
            "approved":   c.approved,
            "attendance": att_pct
        })
    return result


@router.get("/{cadet_id}")
def get_cadet(
    cadet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Any authenticated user can view a single cadet."""
    cadet = db.query(Cadet).filter(Cadet.id == cadet_id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="Cadet not found")
    return {
        "id":       cadet.id,
        "roll_no":  cadet.roll_no,
        "name":     cadet.user.name,
        "email":    cadet.user.email,
        "rank":     cadet.rank,
        "unit":     cadet.unit,
        "approved": cadet.approved
    }


@router.put("/{cadet_id}")
def update_cadet(
    cadet_id: int,
    data: CadetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_officer)
):
    """
    Admin or Officer can update rank and unit.
    Only Admin can change the 'approved' field.
    """
    cadet = db.query(Cadet).filter(Cadet.id == cadet_id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="Cadet not found")

    # Block non-admins from changing approval status
    if data.approved is not None and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only admins can approve or reject cadets"
        )

    if data.rank     is not None: cadet.rank     = data.rank
    if data.unit     is not None: cadet.unit     = data.unit
    if data.approved is not None: cadet.approved = data.approved
    db.commit()
    return {"message": "Cadet updated successfully"}


@router.delete("/{cadet_id}")
def delete_cadet(
    cadet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Only Admin can delete a cadet."""
    cadet = db.query(Cadet).filter(Cadet.id == cadet_id).first()
    if not cadet:
        raise HTTPException(status_code=404, detail="Cadet not found")
    db.query(Attendance).filter(Attendance.cadet_id == cadet_id).delete()
    db.delete(cadet)
    db.commit()
    return {"message": "Cadet deleted"}
