import { useMemo, useState } from "react";
import FindingsList from "./components/FindingsList";
import PrReviewForm from "./components/PrReviewForm";
import ToastStack from "./components/ToastStack";
import { reviewGitHubPR } from "./services/api";

export default function App() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasReviewed, setHasReviewed] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [lastDurationMs, setLastDurationMs] = useState(null);
  const [toasts, setToasts] = useState([]);

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

  async function handleGitHubReview(prUrl, userContext) {
    await runAction(async () => {
      const data = await reviewGitHubPR(prUrl, userContext);
      setFindings(data);
      addToast("success", `Found ${data.length} issue(s).`);
    });
  }

  const summaryText = useMemo(() => {
    if (!hasReviewed || lastDurationMs === null) return "";
    return `Latest review finished in ${formatDuration(lastDurationMs)}.`;
  }, [hasReviewed, lastDurationMs]);

  return (
    <main className="container">
      <header className="header">
        <div className="header-top">
          <div className="brand">
            <span className="brand-icon" aria-hidden="true">
              🤖
            </span>
            <div>
              <h1>Shelby - AI Code Review Agent</h1>
              <p>Minimal, premium PR reviews with focused AI insights</p>
            </div>
          </div>
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
