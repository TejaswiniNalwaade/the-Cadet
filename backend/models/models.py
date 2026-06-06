from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    email       = Column(String(100), unique=True, index=True, nullable=False)
    password    = Column(String(255), nullable=False)       # stored as bcrypt hash
    role        = Column(String(20), default="cadet")       # "officer" or "cadet"
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    cadet       = relationship("Cadet", back_populates="user", uselist=False)


class Cadet(Base):
    __tablename__ = "cadets"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    roll_no     = Column(String(20), unique=True, nullable=False)
    rank        = Column(String(30), default="Cadet")       # Cadet / Private / Corporal / Sergeant
    unit        = Column(String(50), default="Alpha Company")
    approved    = Column(Boolean, default=False)            # Officer must approve

    user        = relationship("User", back_populates="cadet")
    attendance  = relationship("Attendance", back_populates="cadet")


class Attendance(Base):
    __tablename__ = "attendance"

    id          = Column(Integer, primary_key=True, index=True)
    cadet_id    = Column(Integer, ForeignKey("cadets.id"), nullable=False)
    date        = Column(Date, nullable=False)
    status      = Column(String(10), default="present")     # present / absent / leave
    marked_by   = Column(Integer, ForeignKey("users.id"))   # officer who marked

    cadet       = relationship("Cadet", back_populates="attendance")


class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    date        = Column(Date, nullable=False)
    venue       = Column(String(100))
    type        = Column(String(30), default="Parade")      # Parade / Camp / Drill / Ceremony
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class Announcement(Base):
    __tablename__ = "announcements"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(150), nullable=False)
    body        = Column(Text, nullable=False)
    posted_by   = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
