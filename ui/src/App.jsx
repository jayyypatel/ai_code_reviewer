import { useEffect, useMemo, useState } from "react";
import FindingsList from "./components/FindingsList";
import PrReviewForm from "./components/PrReviewForm";
import ThemeToggle from "./components/ThemeToggle";
import ToastStack from "./components/ToastStack";
import { reviewGitHubPR } from "./services/api";

const THEME_KEY = "ai-reviewer-theme";

export default function App() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasReviewed, setHasReviewed] = useState(false);
  const [theme, setTheme] = useState("light");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [lastDurationMs, setLastDurationMs] = useState(null);
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const stored = window.localStorage.getItem(THEME_KEY);
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
      return;
    }
    const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  function addToast(type, message) {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, type, message }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 3800);
  }

  function formatDuration(ms) {
    return `${(ms / 1000).toFixed(1)}s`;
  }

  async function runAction(action) {
    const startedAt = Date.now();
    setLoading(true);
    setElapsedMs(0);
    setLastDurationMs(null);
    const interval = window.setInterval(() => {
      setElapsedMs(Date.now() - startedAt);
    }, 100);
    try {
      await action();
      const duration = Date.now() - startedAt;
      setLastDurationMs(duration);
      addToast("success", `Review completed in ${formatDuration(duration)}.`);
      setHasReviewed(true);
    } catch (err) {
      const duration = Date.now() - startedAt;
      setLastDurationMs(duration);
      addToast("error", err.message || "Unexpected error.");
      setHasReviewed(true);
    } finally {
      window.clearInterval(interval);
      setElapsedMs(Date.now() - startedAt);
      setLoading(false);
    }
  }

  async function handleGitHubReview(repo, pullNumber) {
    await runAction(async () => {
      const data = await reviewGitHubPR(repo, pullNumber);
      setFindings(data);
      addToast("success", `Found ${data.length} issue(s).`);
    });
  }

  const summaryText = useMemo(() => {
    if (!hasReviewed || lastDurationMs === null) return "";
    return `Latest review finished in ${formatDuration(lastDurationMs)}.`;
  }, [hasReviewed, lastDurationMs]);

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  return (
    <main className="container">
      <header className="header">
        <div className="header-top">
          <div className="brand">
            <span className="brand-icon" aria-hidden="true">
              🤖
            </span>
            <div>
              <h1>AI Code Review Agent</h1>
              <p>Review GitHub pull requests with AI insights</p>
            </div>
          </div>
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
        <div className="header-backdrop" aria-hidden="true" />
      </header>

      <PrReviewForm onSubmit={handleGitHubReview} loading={loading} elapsedMs={elapsedMs} />
      {summaryText ? <p className="muted status-line">{summaryText}</p> : null}

      <FindingsList findings={findings} loading={loading} hasReviewed={hasReviewed} />
      <ToastStack toasts={toasts} />
    </main>
  );
}
