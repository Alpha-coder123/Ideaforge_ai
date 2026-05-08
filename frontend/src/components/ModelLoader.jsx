import { useState } from "react";

const RECOMMENDED_MODELS = [
  {
    id: "google/flan-t5-base",
    label: "Flan-T5 Base",
    size: "~250MB",
    ram: "~1GB",
    speed: "⚡ Fast",
    note: "Best for low-end machines & testing",
    recommended: true,
    tier: 1,
  },
  {
    id: "google/flan-t5-large",
    label: "Flan-T5 Large",
    size: "~780MB",
    ram: "~2GB",
    speed: "⚡ Fast",
    note: "Better quality, still lightweight",
    recommended: false,
    tier: 1,
  },
  {
    id: "google/flan-t5-xl",
    label: "Flan-T5 XL",
    size: "~3GB",
    ram: "~5GB",
    speed: "◑ Moderate",
    note: "High quality seq2seq output",
    recommended: false,
    tier: 2,
  },
  {
    id: "Qwen/Qwen2-0.5B-Instruct",
    label: "Qwen2 0.5B",
    size: "~1GB",
    ram: "~2GB",
    speed: "⚡ Fast",
    note: "Surprisingly capable for its size",
    recommended: false,
    tier: 1,
  },
  {
    id: "Qwen/Qwen2-1.5B-Instruct",
    label: "Qwen2 1.5B",
    size: "~3GB",
    ram: "~4GB",
    speed: "◑ Moderate",
    note: "Great balance of speed & quality",
    recommended: false,
    tier: 2,
  },
  {
    id: "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    label: "TinyLlama 1.1B",
    size: "~2.2GB",
    ram: "~3GB",
    speed: "◑ Moderate",
    note: "Good conversational quality",
    recommended: false,
    tier: 2,
  },
  {
    id: "microsoft/phi-2",
    label: "Microsoft Phi-2",
    size: "~5.5GB",
    ram: "~6GB",
    speed: "◔ Slow on CPU",
    note: "High quality reasoning",
    recommended: false,
    tier: 3,
  },
];

// Compact inline panel for switching model mid-session
export function ModelSwitcher({ currentModel, onLoaded }) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(currentModel || "google/flan-t5-base");
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const modelToLoad = custom.trim() || selected;

  const handleLoad = async () => {
    if (modelToLoad === currentModel) {
      setOpen(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `http://localhost:8000/api/load-model?model_name=${encodeURIComponent(modelToLoad)}`,
        { method: "POST" }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load model");
      onLoaded({ model: data.model, device: data.device });
      setOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button className="model-switch-btn" onClick={() => setOpen(true)}>
        <span className="model-switch-icon">⬡</span>
        <span>Switch Model</span>
        <span className="model-switch-chevron">›</span>
      </button>
    );
  }

  return (
    <div className="model-switcher-panel">
      <div className="switcher-header">
        <span className="switcher-title">⬡ Change Model</span>
        <button className="switcher-close" onClick={() => setOpen(false)}>✕</button>
      </div>

      <div className="switcher-grid">
        {RECOMMENDED_MODELS.map((m) => (
          <div
            key={m.id}
            className={`switcher-card ${selected === m.id && !custom ? "active" : ""} ${m.id === currentModel ? "current" : ""}`}
            onClick={() => { setSelected(m.id); setCustom(""); }}
          >
            {m.recommended && <span className="rec-badge">Recommended</span>}
            {m.id === currentModel && <span className="current-badge">Active</span>}
            <div className="switcher-card-name">{m.label}</div>
            <div className="switcher-card-meta">
              <span>{m.ram}</span>
              <span className="dot-sep">·</span>
              <span className="speed-tag">{m.speed}</span>
            </div>
            <div className="switcher-card-note">{m.note}</div>
          </div>
        ))}
      </div>

      <div className="switcher-custom">
        <label className="input-label">→ Custom HuggingFace model ID</label>
        <input
          className="custom-input"
          placeholder="e.g. mistralai/Mistral-7B-Instruct-v0.1"
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          disabled={loading}
        />
      </div>

      {error && <div className="error-banner">⚠ {error}</div>}

      <button
        className="run-btn"
        onClick={handleLoad}
        disabled={loading || !modelToLoad}
        style={{ width: "100%", justifyContent: "center", marginTop: 4 }}
      >
        {loading ? (
          <><span className="spin">◈</span> Loading Model...</>
        ) : modelToLoad === currentModel ? (
          "Already loaded — close panel"
        ) : (
          `⬡ Load "${modelToLoad}"`
        )}
      </button>
    </div>
  );
}

// Full-page loader shown on first visit
export default function ModelLoader({ onLoaded }) {
  const [selected, setSelected] = useState("google/flan-t5-base");
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingMsg, setLoadingMsg] = useState("");

  const modelToLoad = custom.trim() || selected;

  const handleLoad = async () => {
    setLoading(true);
    setError("");
    setLoadingMsg(
      `Downloading and loading "${modelToLoad}"…\nThis may take a few minutes on first run (model is cached after).`
    );

    try {
      const res = await fetch(
        `http://localhost:8000/api/load-model?model_name=${encodeURIComponent(modelToLoad)}`,
        { method: "POST" }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load model");
      onLoaded({ model: data.model, device: data.device });
    } catch (err) {
      setError(err.message);
      setLoadingMsg("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="model-loader">
      <div className="loader-header">
        <span className="loader-icon">⬡</span>
        <h2>Load a Local Model</h2>
      </div>
      <p className="loader-sub">
        IdeaForge runs entirely on your machine — no cloud APIs, no data sent anywhere.
        Select a HuggingFace model to download and run locally. Models are cached after the first download.
      </p>

      <div className="loader-tier-label">Lightweight (CPU-friendly)</div>
      <div className="model-grid">
        {RECOMMENDED_MODELS.filter(m => m.tier === 1).map((m) => (
          <ModelCard key={m.id} m={m} selected={selected} custom={custom}
            onSelect={() => { setSelected(m.id); setCustom(""); }} />
        ))}
      </div>

      <div className="loader-tier-label" style={{ marginTop: 16 }}>Mid-weight (4–6GB RAM)</div>
      <div className="model-grid">
        {RECOMMENDED_MODELS.filter(m => m.tier === 2).map((m) => (
          <ModelCard key={m.id} m={m} selected={selected} custom={custom}
            onSelect={() => { setSelected(m.id); setCustom(""); }} />
        ))}
      </div>

      <div className="loader-tier-label" style={{ marginTop: 16 }}>Heavy (GPU recommended)</div>
      <div className="model-grid">
        {RECOMMENDED_MODELS.filter(m => m.tier === 3).map((m) => (
          <ModelCard key={m.id} m={m} selected={selected} custom={custom}
            onSelect={() => { setSelected(m.id); setCustom(""); }} />
        ))}
      </div>

      <div className="custom-model">
        <label className="input-label">→ Or enter any HuggingFace model ID</label>
        <input
          className="custom-input"
          placeholder="e.g. mistralai/Mistral-7B-Instruct-v0.1"
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          disabled={loading}
        />
      </div>

      {error && <div className="error-banner">⚠ {error}</div>}

      {loadingMsg && (
        <div className="loading-log">
          <pre>{loadingMsg}</pre>
          <div className="loading-spinner">◈ Loading model, please wait…</div>
        </div>
      )}

      <button
        className="run-btn"
        onClick={handleLoad}
        disabled={loading || !modelToLoad}
        style={{ width: "100%", justifyContent: "center" }}
      >
        {loading ? (
          <><span className="spin">◈</span> Loading Model…</>
        ) : (
          `⬡ Load "${modelToLoad}"`
        )}
      </button>
    </div>
  );
}

function ModelCard({ m, selected, custom, onSelect }) {
  const isActive = selected === m.id && !custom;
  return (
    <div
      className={`model-card ${isActive ? "active" : ""}`}
      onClick={onSelect}
    >
      {m.recommended && <span className="rec-badge">Recommended</span>}
      <div className="model-card-name">{m.label}</div>
      <div className="model-card-meta">
        <span>{m.size}</span>
        <span>·</span>
        <span>{m.ram} RAM</span>
        <span>·</span>
        <span className="model-speed">{m.speed}</span>
      </div>
      <div className="model-card-note">{m.note}</div>
      <div className="model-card-id">{m.id}</div>
    </div>
  );
}
