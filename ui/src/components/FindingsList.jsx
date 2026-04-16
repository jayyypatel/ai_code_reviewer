import FindingCard from "./FindingCard";

export default function FindingsList({ findings, loading, hasReviewed }) {
  if (loading) {
    return (
      <section className="findings-panel fade-in">
        <h3>Findings</h3>
        <div className="skeleton-list">
          <div className="skeleton-card" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
        </div>
      </section>
    );
  }

  if (!hasReviewed) return null;

  return (
    <section className="findings-panel fade-in">
      <h3>Findings ({findings.length})</h3>
      {!findings.length ? (
        <p className="muted">No issues found in changed lines.</p>
      ) : (
        <div className="findings-list">
          {findings.map((finding, index) => (
            <FindingCard key={`${finding.file}-${finding.title}-${index}`} finding={finding} index={index} />
          ))}
        </div>
      )}
    </section>
  );
}
