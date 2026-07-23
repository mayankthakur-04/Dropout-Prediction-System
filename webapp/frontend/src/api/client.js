// ==========================================================================
// API CLIENT
// Centralizes all calls to the FastAPI backend. Handles attaching the JWT
// token to requests and basic error handling so components don't repeat
// this logic everywhere.
// ==========================================================================

// Change this if your backend runs on a different port/host.
const API_BASE_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function clearToken() {
  localStorage.removeItem("access_token");
}

/**
 * Generic authenticated fetch wrapper. Throws an Error with a readable
 * message on failure, so calling code can show it to the user.
 */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const errBody = await response.json();
      detail = errBody.detail || detail;
    } catch {
      // response had no JSON body; keep default message
    }
    throw new Error(detail);
  }

  return response.json();
}

// --------------------------------------------------------------------
// Auth
// --------------------------------------------------------------------
export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    let detail = "Login failed. Please check your username and password.";
    try {
      const errBody = await response.json();
      detail = errBody.detail || detail;
    } catch {
      // keep default message
    }
    throw new Error(detail);
  }

  const data = await response.json();
  setToken(data.access_token);
  localStorage.setItem("user_role", data.role);
  localStorage.setItem("user_full_name", data.full_name);
  localStorage.setItem("user_username", data.username);
  return data;
}

export function logout() {
  clearToken();
  localStorage.removeItem("user_role");
  localStorage.removeItem("user_full_name");
  localStorage.removeItem("user_username");
}

export function isLoggedIn() {
  return !!getToken();
}

export function getCurrentUserFromStorage() {
  if (!isLoggedIn()) return null;
  return {
    role: localStorage.getItem("user_role"),
    full_name: localStorage.getItem("user_full_name"),
    username: localStorage.getItem("user_username"),
  };
}

// --------------------------------------------------------------------
// Dashboard data
// --------------------------------------------------------------------
export function getOverview() {
  return apiFetch("/api/overview");
}

export function getStudents({ riskTier, search } = {}) {
  const params = new URLSearchParams();
  if (riskTier && riskTier !== "All") params.append("risk_tier", riskTier);
  if (search) params.append("search", search);
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiFetch(`/api/students${query}`);
}

export function getStudent(studentId) {
  return apiFetch(`/api/students/${encodeURIComponent(studentId)}`);
}

export function getStudentRecommendations(studentId) {
  return apiFetch(`/api/students/${encodeURIComponent(studentId)}/recommendations`);
}

export function getAlerts(limit = 50) {
  return apiFetch(`/api/alerts?limit=${limit}`);
}

export function getFeatureImportance() {
  return apiFetch("/api/feature-importance");
}

export function getModelMetrics() {
  return apiFetch("/api/model-metrics");
}

export function predictNewStudent(payload) {
  return apiFetch("/api/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAdminUsers() {
  return apiFetch("/api/admin/users");
}
