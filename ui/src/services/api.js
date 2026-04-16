const JSON_HEADERS = {
  "Content-Type": "application/json"
};

const REQUEST_TIMEOUT_MS = 180000;
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");

function withBase(path) {
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path}`;
}

function extractErrorMessage(data, status) {
  if (!data) {
    return `Request failed with status ${status}.`;
  }

  if (typeof data.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (Array.isArray(data)) {
    const first = data.find((item) => typeof item === "string" && item.trim());
    if (first) return first;
  }

  if (typeof data === "object") {
    const entries = Object.entries(data);
    const fieldErrors = entries
      .map(([field, value]) => {
        if (Array.isArray(value)) {
          return `${field}: ${value.join(", ")}`;
        }
        if (typeof value === "string") {
          return `${field}: ${value}`;
        }
        return null;
      })
      .filter(Boolean);

    if (fieldErrors.length) {
      return fieldErrors.join(" | ");
    }
  }

  return `Request failed with status ${status}.`;
}

async function request(url, payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify(payload),
      signal: controller.signal
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timed out after 180 seconds.");
    }
    throw new Error("Network error. Check backend server and try again.");
  } finally {
    clearTimeout(timeoutId);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message = extractErrorMessage(data, response.status);
    throw new Error(message);
  }

  return data;
}

export function reviewGitHubPR(prUrl, userContext = "") {
  return request(withBase("/github-review/"), {
    pr_url: prUrl,
    user_context: userContext
  });
}
