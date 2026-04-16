import { useState } from "react";

const INITIAL_COMMENT_STATE = {
  repo: "",
  pull_number: "",
  body: "",
  path: "",
  line: "",
  commit_id: ""
};

export default function ReviewForms({
  onCodeReview,
  onGitHubReview,
  onGitHubComment,
  loading
}) {
  const [code, setCode] = useState("");
  const [repo, setRepo] = useState("");
  const [pullNumber, setPullNumber] = useState("");
  const [commentData, setCommentData] = useState(INITIAL_COMMENT_STATE);

  function handleCommentChange(event) {
    const { name, value } = event.target;
    setCommentData((prev) => ({ ...prev, [name]: value }));
  }

  function submitCodeReview(event) {
    event.preventDefault();
    onCodeReview(code);
  }

  function submitGitHubReview(event) {
    event.preventDefault();
    onGitHubReview(repo, pullNumber);
  }

  function submitGitHubComment(event) {
    event.preventDefault();

    const payload = {
      repo: commentData.repo,
      pull_number: Number(commentData.pull_number),
      body: commentData.body
    };

    if (commentData.path && commentData.line && commentData.commit_id) {
      payload.path = commentData.path;
      payload.line = Number(commentData.line);
      payload.commit_id = commentData.commit_id;
    }

    onGitHubComment(payload);
  }

  return (
    <div className="form-grid">
      <section className="panel">
        <h2>Raw Code Review</h2>
        <form onSubmit={submitCodeReview}>
          <label htmlFor="code-input">Code</label>
          <textarea
            id="code-input"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Paste code to review..."
            rows={12}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Reviewing..." : "Review Code"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>GitHub PR Review</h2>
        <form onSubmit={submitGitHubReview}>
          <label htmlFor="repo-input">Repository (owner/repo)</label>
          <input
            id="repo-input"
            value={repo}
            onChange={(event) => setRepo(event.target.value)}
            placeholder="owner/repo"
            required
          />
          <label htmlFor="pull-number-input">Pull Request Number</label>
          <input
            id="pull-number-input"
            type="number"
            min="1"
            value={pullNumber}
            onChange={(event) => setPullNumber(event.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Reviewing..." : "Review PR"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Post GitHub Comment (Optional)</h2>
        <form onSubmit={submitGitHubComment}>
          <label htmlFor="comment-repo-input">Repository (owner/repo)</label>
          <input
            id="comment-repo-input"
            name="repo"
            value={commentData.repo}
            onChange={handleCommentChange}
            required
          />
          <label htmlFor="comment-pr-input">Pull Request Number</label>
          <input
            id="comment-pr-input"
            type="number"
            min="1"
            name="pull_number"
            value={commentData.pull_number}
            onChange={handleCommentChange}
            required
          />
          <label htmlFor="comment-body-input">Comment Body</label>
          <textarea
            id="comment-body-input"
            name="body"
            value={commentData.body}
            onChange={handleCommentChange}
            rows={4}
            required
          />
          <label htmlFor="comment-path-input">Path (optional for inline comment)</label>
          <input
            id="comment-path-input"
            name="path"
            value={commentData.path}
            onChange={handleCommentChange}
            placeholder="src/file.py"
          />
          <label htmlFor="comment-line-input">Line (optional for inline comment)</label>
          <input
            id="comment-line-input"
            type="number"
            min="1"
            name="line"
            value={commentData.line}
            onChange={handleCommentChange}
          />
          <label htmlFor="comment-commit-input">Commit SHA (optional for inline comment)</label>
          <input
            id="comment-commit-input"
            name="commit_id"
            value={commentData.commit_id}
            onChange={handleCommentChange}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Posting..." : "Post Comment"}
          </button>
        </form>
      </section>
    </div>
  );
}
