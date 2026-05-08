export default function ThreadInput({
  thread,
  setThread,
  rounds,
  setRounds,
  onRun,
  onReset,
  status,
}) {
  const isRunning = status === "running";
  const isDone = status === "done";

  return (
    <div className="input-section">
      <label className="input-label">→ Enter your idea thread</label>
      <textarea
        className="thread-input"
        value={thread}
        onChange={(e) => setThread(e.target.value)}
        placeholder="e.g. A mobile app that helps people with ADHD build habits using gamification and AI coaching..."
        disabled={isRunning}
        rows={4}
      />

      <div className="input-controls">
        <div className="rounds-control">
          <label className="rounds-label">Discussion Rounds</label>
          <div className="rounds-buttons">
            {[1, 2, 3].map((r) => (
              <button
                key={r}
                className={`round-btn ${rounds === r ? "active" : ""}`}
                onClick={() => setRounds(r)}
                disabled={isRunning}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className="action-buttons">
          <button
            className="run-btn"
            onClick={onRun}
            disabled={isRunning || !thread.trim()}
          >
            {isRunning ? (
              <>
                <span className="spin">◈</span> Agents Thinking...
              </>
            ) : (
              <>◈ Run Discussion</>
            )}
          </button>

          {isDone && (
            <button className="new-btn" onClick={onReset}>
              ↺ New Thread
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
