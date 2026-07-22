/* ============================================================================
   API client
   Change API_BASE if the Flask backend runs somewhere other than localhost:5000
   ============================================================================ */
// const API_BASE = "http://10.129.188.47:9696/api";
const API_BASE = "http://127.0.0.1:9696/api";

const Auth = {
  getToken() { return localStorage.getItem("armsToken"); },
  getUser() {
    const raw = localStorage.getItem("armsUser");
    return raw ? JSON.parse(raw) : null;
  },
  setSession(token, user) {
    localStorage.setItem("armsToken", token);
    localStorage.setItem("armsUser", JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem("armsToken");
    localStorage.removeItem("armsUser");
  },
  requireLogin() {
    if (!this.getToken()) { window.location.href = "index.html"; }
  },
  logout() {
    this.clear();
    window.location.href = "index.html";
  },
};

/**
 * api(path, { method, json, form, params })
 * - json: plain object -> sent as application/json
 * - form: FormData -> sent as multipart (for the Raise Request attachment)
 * - params: object -> appended as query string
 */
async function api(path, { method = "GET", json, form, params, raw } = {}) {
  let url = `${API_BASE}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== ""))
    ).toString();
    if (qs) url += `?${qs}`;
  }

  const headers = {};
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(json);
  } else if (form !== undefined) {
    options.body = form; // browser sets multipart boundary automatically
  }

  const res = await fetch(url, options);

  if (res.status === 401) {
    Auth.clear();
    window.location.href = "index.html";
    throw new Error("Session expired");
  }

  if (raw) return res; // caller wants the raw Response (e.g. file download)

  const contentType = res.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await res.json() : await res.text();

  if (!res.ok) {
    const message = (body && body.error) ? body.error : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return body;
}

function showToast(message, type = "") {
  const el = document.createElement("div");
  el.className = `toast ${type ? "toast--" + type : ""}`;
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function fmtDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function statusClass(status) {
  if (["Rejected"].includes(status)) return "status--rejected";
  if (["Closed", "Production"].includes(status)) return status === "Closed" ? "status--closed" : "status--approved";
  if (["Pending Platform Approval", "Pending PGC Approval"].includes(status)) return "status--pending";
  if (["In Development", "Testing/UAT"].includes(status)) return "status--progress";
  return "status--pending";
}

function reqCode(id) { return `REQ-${String(id).padStart(4, "0")}`; }
