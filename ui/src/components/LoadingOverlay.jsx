export default function LoadingOverlay({ message }) {
  return (
    <div className="loading-overlay" role="status" aria-live="polite" aria-busy="true">
      <div className="loading-card">
        <div className="spinner" />
        <p className="loading-title">Processing your request</p>
        <p className="loading-subtitle">{message || "Please wait..."}</p>
      </div>
    </div>
  );
}
