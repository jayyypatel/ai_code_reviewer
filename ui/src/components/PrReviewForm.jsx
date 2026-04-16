import { useState } from "react";

const REPO_PATTERN = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

export default function PrReviewForm({ loading, elapsedMs, onSubmit }) {
  const [repo, setRepo] = useState("");
  const [pullNumber, setPullNumber] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const normalizedRepo = repo.trim();
    const normalizedPr = pullNumber.trim();

    if (!REPO_PATTERN.test(normalizedRepo)) {
      setError("Repository must be in owner/repo format.");
      return;
    }
    if (!/^\d+$/.test(normalizedPr) || Number(normalizedPr) < 1) {
      setError("PR number must be a positive number.");
      return;
    }

    setError("");
    onSubmit(normalizedRepo, normalizedPr);
  }

  function formatSeconds(ms) {
    return (ms / 1000).toFixed(1);
  }

  return (
    <section className="pr-card">
      <h2>GitHub PR Review</h2>
      <p className="section-subtitle">
        Enter repository and PR number. The review runs only on changed lines.
      </p>
      <form className="pr-form" onSubmit={handleSubmit}>
        <label htmlFor="repo-input">Repository</label>
        <input
          id="repo-input"
          type="text"
          placeholder="odoo/odoo"
          value={repo}
          onChange={(event) => setRepo(event.target.value)}
          autoComplete="off"
          required
        />

        <label htmlFor="pr-input">Pull Request Number</label>
        <input
          id="pr-input"
          type="number"
          min="1"
          placeholder="259464"
          value={pullNumber}
          onChange={(event) => setPullNumber(event.target.value)}
          required
        />

        {error ? <p className="error form-error">{error}</p> : null}

        <p className="helper-text">Format: owner/repo (example: odoo/odoo)</p>

        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? (
            <span className="btn-loading">
              <span className="btn-spinner" />
              Reviewing PR
            </span>
          ) : (
            "Review PR"
          )}
        </button>
        {loading ? <p className="timer-text">Elapsed: {formatSeconds(elapsedMs)}s</p> : null}
      </form>
    </section>
  );
}
