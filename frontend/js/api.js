// Base URL of your FastAPI backend
const API = "https://the-cadet.onrender.com";

// ── Token helpers ─────────────────────────────────────────────────────────
function getToken()  { return localStorage.getItem("ncc_token"); }
function getRole()   { return localStorage.getItem("ncc_role"); }
function getName()   { return localStorage.getItem("ncc_name"); }
function getUserId() { return localStorage.getItem("ncc_user_id"); }

function authHeaders() {
  return {
    "Content-Type":  "application/json",
    "Authorization": "Bearer " + getToken()
  };
}

// Redirect to login if not logged in
function requireAuth() {
  if (!getToken()) window.location.href = "../index.html";
}

// Redirect non-admin away from admin-only pages
function requireAdmin() {
  if (!getToken()) { window.location.href = "../index.html"; return; }
  const role = getRole();
  if (role !== "admin") {
    // Cadets/officers get bounced back to dashboard
    window.location.href = "dashboard.html";
  }
}

// ── Auth calls ────────────────────────────────────────────────────────────
async function apiLogin(email, password) {
  const res  = await fetch(`${API}/auth/login`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email, password })
  });
  return res.json();
}

async function apiRegister(data) {
  // Always strips role — backend enforces cadet-only registration
  const safeData = { name: data.name, email: data.email, password: data.password, roll_no: data.roll_no || "", unit: data.unit || "Alpha Company" };
  const res = await fetch(`${API}/auth/register`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(safeData)
  });
  return res.json();
}

// ── Cadet calls ───────────────────────────────────────────────────────────
async function apiGetCadets() {
  const res = await fetch(`${API}/cadets/`, { headers: authHeaders() });
  return res.json();
}

async function apiUpdateCadet(id, data) {
  const res = await fetch(`${API}/cadets/${id}`, {
    method:  "PUT",
    headers: authHeaders(),
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function apiDeleteCadet(id) {
  const res = await fetch(`${API}/cadets/${id}`, {
    method:  "DELETE",
    headers: authHeaders()
  });
  return res.json();
}

// ── Attendance calls ──────────────────────────────────────────────────────
async function apiGetAttendanceByDate(date) {
  const res = await fetch(`${API}/attendance/date/${date}`, { headers: authHeaders() });
  return res.json();
}

async function apiMarkAttendance(date, entries) {
  const res = await fetch(`${API}/attendance/mark`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify({ date, entries })
  });
  return res.json();
}

// Cadet: fetch own attendance only
async function apiGetMyAttendance() {
  const res = await fetch(`${API}/attendance/my`, { headers: authHeaders() });
  return res.json();
}

// ── Events calls ──────────────────────────────────────────────────────────
async function apiGetEvents() {
  const res = await fetch(`${API}/events/`, { headers: authHeaders() });
  return res.json();
}

async function apiCreateEvent(data) {
  const res = await fetch(`${API}/events/`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function apiDeleteEvent(id) {
  const res = await fetch(`${API}/events/${id}`, {
    method:  "DELETE",
    headers: authHeaders()
  });
  return res.json();
}

// ── Announcement calls ────────────────────────────────────────────────────
async function apiGetAnnouncements() {
  const res = await fetch(`${API}/events/announcements`, { headers: authHeaders() });
  return res.json();
}

async function apiCreateAnnouncement(data) {
  const res = await fetch(`${API}/events/announcements`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function apiDeleteAnnouncement(id) {
  const res = await fetch(`${API}/events/announcements/${id}`, {
    method:  "DELETE",
    headers: authHeaders()
  });
  return res.json();
}

// ── Admin calls ───────────────────────────────────────────────────────────
async function apiAdminStats() {
  const res = await fetch(`${API}/admin/stats`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminGetUsers() {
  const res = await fetch(`${API}/admin/users`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminCreateUser(data) {
  const res = await fetch(`${API}/admin/users`, {
    method:  "POST",
    headers: authHeaders(),
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function apiAdminUpdateUser(id, data) {
  const res = await fetch(`${API}/admin/users/${id}`, {
    method:  "PUT",
    headers: authHeaders(),
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function apiAdminDeleteUser(id) {
  const res = await fetch(`${API}/admin/users/${id}`, {
    method:  "DELETE",
    headers: authHeaders()
  });
  return res.json();
}

async function apiAdminApproveCadet(cadetId) {
  const res = await fetch(`${API}/admin/cadets/${cadetId}/approve`, {
    method:  "POST",
    headers: authHeaders()
  });
  return res.json();
}

async function apiAdminRejectCadet(cadetId) {
  const res = await fetch(`${API}/admin/cadets/${cadetId}/reject`, {
    method:  "POST",
    headers: authHeaders()
  });
  return res.json();
}
