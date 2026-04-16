import { useState } from "react";

const SEVERITY_META = {
  high: { icon: "🔴", label: "High", className: "severity-high" },
  medium: { icon: "🟡", label: "Medium", className: "severity-medium" },
  low: { icon: "🔵", label: "Low", className: "severity-low" }
};

export default function FindingCard({ finding, index }) {
  const [open, setOpen] = useState(index === 0);
  const [copied, setCopied] = useState(false);
  const meta = SEVERITY_META[finding.severity] || SEVERITY_META.low;
  const location = finding.line ? `${finding.file}:${finding.line}` : finding.file || "Unknown file";

  async function copyFixedCode() {
    if (!finding.fixed_code) return;
    await navigator.clipboard.writeText(finding.fixed_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  }

  return (
    <article className={`finding-item ${meta.className}`}>
      <button
        className="finding-toggle"
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
      >
        <span className="finding-title-wrap">
          <span>{meta.icon}</span>
          <span className="finding-title">{finding.title || "Code quality finding"}</span>
        </span>
        <span className={`severity-badge ${meta.className}`}>{meta.label}</span>
      </button>

      {open ? (
        <div className="finding-body">
          <p className="finding-location">{location}</p>
          <p className="finding-text">
            <strong>Explanation:</strong> {finding.explanation || "No explanation provided."}
          </p>
          <p className="finding-text">
            <strong>Suggestion:</strong> {finding.suggestion || "No suggestion provided."}
          </p>

          {finding.fixed_code ? (
            <div className="fixed-code-block">
              <div className="fixed-code-header">
                <strong>Fixed code</strong>
                <button className="ghost-btn" type="button" onClick={copyFixedCode}>
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
              <pre>{finding.fixed_code}</pre>
            </div>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}
