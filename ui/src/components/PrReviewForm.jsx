import { useState } from "react";

const PR_URL_PATTERN = /^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+\/pull\/\d+\/?$/i;

export default function PrReviewForm({ loading, elapsedMs, onSubmit }) {
  const [prUrl, setPrUrl] = useState("");
  const [userContext, setUserContext] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const normalizedUrl = prUrl.trim();

    if (!PR_URL_PATTERN.test(normalizedUrl)) {
      setError("Enter a valid GitHub PR URL like https://github.com/owner/repo/pull/123.");
      return;
    }

    setError("");
    onSubmit(normalizedUrl, userContext.trim());
  }

  function formatSeconds(ms) {
    return (ms / 1000).toFixed(1);
  }

  return (
    <section className="pr-card">
      <h2>GitHub PR Review</h2>
      <p className="section-subtitle">
        Paste the PR URL. Shelby auto-extracts owner, repo, and PR number.
      </p>
      <form className="pr-form" onSubmit={handleSubmit}>
        <label htmlFor="pr-url-input">Pull Request URL</label>
        <input
          id="pr-url-input"
          type="text"
          placeholder="https://github.com/odoo/odoo/pull/259464"
          value={prUrl}
          onChange={(event) => setPrUrl(event.target.value)}
          autoComplete="off"
          required
        />

        <label htmlFor="context-input">Review Context (Optional)</label>
        <textarea
          id="context-input"
          rows={4}
          placeholder="Example: focus on security, data consistency, and backward compatibility."
          value={userContext}
          onChange={(event) => setUserContext(event.target.value)}
        />

        {error ? <p className="error form-error">{error}</p> : null}

        <p className="helper-text">Tip: Add context to get more targeted findings from Shelby.</p>

        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? (
            <span className="btn-loading">
              <span className="btn-spinner" />
              Shelby is reviewing
            </span>
          ) : (
            "Review PR"
          )}
        </button>
        {loading ? <p className="timer-text">Elapsed: {formatSeconds(elapsedMs)}s</p> : null}
        {loading ? (
          <div className="loading-wave" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        ) : null}
      </form>
    </section>
  );
}
