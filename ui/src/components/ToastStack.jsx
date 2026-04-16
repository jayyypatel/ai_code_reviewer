export default function ToastStack({ toasts }) {
  if (!toasts.length) return null;

  return (
    <aside className="toast-stack" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <article key={toast.id} className={`toast toast-${toast.type}`}>
          <span className="toast-icon" aria-hidden="true">
            {toast.type === "success" ? "✅" : "⚠️"}
          </span>
          <p>{toast.message}</p>
        </article>
      ))}
    </aside>
  );
}
