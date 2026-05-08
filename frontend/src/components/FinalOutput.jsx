import { useEffect, useState } from "react";

export default function FinalOutput({ output }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
  };

  return (
    <div className={`final-output-section ${visible ? "visible" : ""}`}>
      <div className="section-header" style={{ marginTop: 32 }}>
        <span className="section-label">Synthesized Output</span>
        <div className="section-line" />
        <button className="copy-btn" onClick={handleCopy}>
          ⎘ Copy
        </button>
      </div>

      <div className="final-output">
        <div className="final-header">
          <span className="final-icon">◉</span>
          <h2>Synthesized Idea</h2>
        </div>
        <div className="final-content">
          {output.split("\n").map((line, i) => (
            <p
              key={i}
              className={
                line.trim().startsWith("-") ||
                /^\d+\./.test(line.trim())
                  ? "final-list-item"
                  : ""
              }
            >
              {line}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
