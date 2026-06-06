from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from models.models import Event, Announcement, User
from routers.deps import get_current_user, require_admin

router = APIRouter()

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    name:       str
    date:       date
    venue:      Optional[str] = ""
    type:       Optional[str] = "Parade"
    created_by: Optional[int] = None

class AnnouncementCreate(BaseModel):
    title:     str
    body:      str
    posted_by: Optional[int] = None

# ── Announcement routes ───────────────────────────────────────────────────────

@router.get("/announcements")
def get_announcements(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)   # 🔒 Must be logged in to read
):
    items = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return [
        {
            "id":         a.id,
            "title":      a.title,
            "body":       a.body,
            "created_at": str(a.created_at)
        }
        for a in items
    ]

@router.post("/announcements")
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    ann = Announcement(
        title     = data.title,
        body      = data.body,
        posted_by = current_user.id
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return {"message": "Announcement posted", "id": ann.id}

@router.delete("/announcements/{ann_id}")
def delete_announcement(
    ann_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    ann = db.query(Announcement).filter(Announcement.id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(ann)
    db.commit()
    return {"message": "Announcement deleted"}

# ── Event routes ──────────────────────────────────────────────────────────────

@router.get("/")
def get_events(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)   # 🔒 Must be logged in
):
    events = db.query(Event).order_by(Event.date).all()
    return [
        {
            "id":    e.id,
            "name":  e.name,
            "date":  str(e.date),
            "venue": e.venue,
            "type":  e.type
        }
        for e in events
    ]

@router.post("/")
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    event = Event(
        name       = data.name,
        date       = data.date,
        venue      = data.venue,
        type       = data.type,
        created_by = current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"message": "Event created", "id": event.id}

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)   # 🔒 ADMIN ONLY
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
