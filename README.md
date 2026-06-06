# 🎖️ The Cadet — NCC Management System

A full-stack web application for managing NCC (National Cadet Corps) college units.  
Built as a **BCA Final Year Full Stack Project**.

---

## 🚀 Features

- Officer & Cadet Login System (Role-based access)
- Cadet Registration & Profile Management
- Attendance Marking & Tracking
- Event / Parade Management
- Announcements & Notifications
- Analytics Dashboard (Charts)
- Admin approval for new cadets

---

## 🛠 Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Chart.js (for analytics)

### Backend
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- JWT Authentication

---

## 📂 Project Structure

```
ncc-management-system/
├── frontend/
│   ├── index.html          ← Login page
│   ├── pages/
│   │   ├── dashboard.html
│   │   ├── cadets.html
│   │   ├── attendance.html
│   │   ├── events.html
│   │   └── announcements.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js
│       ├── cadets.js
│       ├── attendance.js
│       └── api.js
├── backend/
│   ├── main.py             ← FastAPI app entry point
│   ├── database.py         ← PostgreSQL connection
│   ├── models/
│   │   └── models.py       ← Database table definitions
│   ├── routers/
│   │   ├── auth.py         ← Login / Register routes
│   │   ├── cadets.py       ← Cadet CRUD routes
│   │   ├── attendance.py   ← Attendance routes
│   │   └── events.py       ← Events & Announcements routes
│   └── requirements.txt
└── README.md
```

---

## ⚙️ How to Run

### Step 1 — Setup Database
1. Open pgAdmin (PostgreSQL)
2. Create a new database called `ncc_db`
3. Update the DB URL in `backend/database.py`

### Step 2 — Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

### Step 3 — Run Frontend
Just open `frontend/index.html` in your browser.
Or use VS Code Live Server extension.

### Step 4 — API Docs (Swagger)
Visit: http://localhost:8000/docs

---

## 👨‍💻 Developer

Your Name Here  
BCA Final Year Project — 2025-26
