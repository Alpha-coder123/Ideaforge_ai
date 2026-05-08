export default function ProgressBar({ progress, status }) {
  return (
    <div className="progress-section">
      <div className="progress-label">
        <span>{status === "done" ? "Discussion Complete" : "Discussion in Progress"}</span>
        <span>{progress}%</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
