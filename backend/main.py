from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, cadets, attendance, events
from routers import admin

# Create all tables in PostgreSQL automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NCC Management System API",
    description="Backend API for The Cadet — NCC Management System",
    version="1.0.0"
)

# Allow frontend (HTML files) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route groups
app.include_router(auth.router,       prefix="/auth",        tags=["Authentication"])
app.include_router(cadets.router,     prefix="/cadets",      tags=["Cadets"])
app.include_router(attendance.router, prefix="/attendance",  tags=["Attendance"])
app.include_router(events.router,     prefix="/events",      tags=["Events"])
app.include_router(admin.router,      prefix="/admin",       tags=["Admin"])

@app.get("/")
def root():
    return {"message": "NCC Management System API is running!"}
