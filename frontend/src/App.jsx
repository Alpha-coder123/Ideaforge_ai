import { useState, useEffect, useRef } from "react";
import AgentStrip from "./components/AgentStrip";
import ThreadInput from "./components/ThreadInput";
import ProgressBar from "./components/ProgressBar";
import DiscussionFeed from "./components/DiscussionFeed";
import FinalOutput from "./components/FinalOutput";
import ModelLoader, { ModelSwitcher } from "./components/ModelLoader";
import "./styles/globals.css";

export default function App() {
  const [modelLoaded, setModelLoaded] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [thread, setThread] = useState("");
  const [status, setStatus] = useState("idle"); // idle | running | done | error
  const [messages, setMessages] = useState([]);
  const [finalOutput, setFinalOutput] = useState("");
  const [currentTyping, setCurrentTyping] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [rounds, setRounds] = useState(2);
  const statusRef = useRef(status);
  statusRef.current = status;

  // Check if model is already loaded on mount
  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((r) => r.json())
      .then((data) => {
        if (data.model_loaded) {
          setModelLoaded(true);
          setModelInfo({ model: data.model_name, device: data.device });
        }
      })
      .catch(() => {});
  }, []);

  const runDiscussion = async () => {
    if (!thread.trim() || !modelLoaded) return;

    setStatus("running");
    setMessages([]);
    setFinalOutput("");
    setProgress(0);
    setError("");
    setCurrentTyping(null);

    try {
      const response = await fetch("http://localhost:8000/api/discuss", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread, rounds }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Discussion failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const event = JSON.parse(raw);
            handleEvent(event);
          } catch {}
        }
      }
    } catch (err) {
      setError(err.message);
      setStatus("error");
      setCurrentTyping(null);
    }
  };

  const handleEvent = (event) => {
    switch (event.type) {
      case "discussion_start":
        break;

      case "agent_start":
        setCurrentTyping({
          name: event.agentName,
          role: event.agentRole,
          color: event.agentColor,
          avatar: event.agentAvatar,
        });
        break;

      case "agent_message":
        setCurrentTyping(null);
        setProgress(event.progress || 0);
        setMessages((prev) => [
          ...prev,
          {
            id: `${event.agentId}-r${event.round}-${Date.now()}`,
            agentId: event.agentId,
            agentName: event.agentName,
            agentRole: event.agentRole,
            agentColor: event.agentColor,
            agentAvatar: event.agentAvatar,
            content: event.content,
            round: event.round,
          },
        ]);
        break;

      case "synthesis_start":
        setCurrentTyping({
          name: "Synthesizing",
          role: "Final Idea",
          color: "#26de81",
          avatar: "◉",
        });
        break;

      case "synthesis_done":
        setCurrentTyping(null);
        setProgress(100);
        setFinalOutput(event.content);
        break;

      case "discussion_complete":
        setStatus("done");
        setCurrentTyping(null);
        break;

      case "stream_end":
        if (statusRef.current !== "done") setStatus("done");
        break;
    }
  };

  const reset = () => {
    setStatus("idle");
    setMessages([]);
    setFinalOutput("");
    setThread("");
    setProgress(0);
    setError("");
    setCurrentTyping(null);
  };

  const handleModelLoaded = (info) => {
    setModelLoaded(true);
    setModelInfo(info);
  };

  return (
    <div className="app">
      {/* Background grid effect */}
      <div className="bg-grid" aria-hidden="true" />

      <header className="header">
        <div className="logo-mark">
          <div className="logo-icon">◈</div>
          AI Ideation Platform
        </div>
        <h1>IdeaForge</h1>
        <p>Multi-agent local AI discussion → Best idea synthesis</p>

        {modelInfo && (
          <div className="header-model-bar">
            <div className="model-badge">
              <span className="model-dot" />
              <span>{modelInfo.model}</span>
              <span className="model-badge-sep">·</span>
              <span className="model-device">{modelInfo.device.toUpperCase()}</span>
            </div>
            {status !== "running" && (
              <ModelSwitcher
                currentModel={modelInfo.model}
                onLoaded={handleModelLoaded}
              />
            )}
          </div>
        )}
      </header>

      {!modelLoaded ? (
        <ModelLoader onLoaded={handleModelLoaded} />
      ) : (
        <>
          <AgentStrip />

          <ThreadInput
            thread={thread}
            setThread={setThread}
            rounds={rounds}
            setRounds={setRounds}
            onRun={runDiscussion}
            onReset={reset}
            status={status}
          />

          {error && (
            <div className="error-banner">⚠ {error}</div>
          )}

          {(status === "running" || status === "done") && (
            <ProgressBar progress={progress} status={status} />
          )}

          {status !== "idle" && (
            <DiscussionFeed
              messages={messages}
              currentTyping={currentTyping}
            />
          )}

          {finalOutput && <FinalOutput output={finalOutput} />}

          {status === "idle" && (
            <div className="empty-state">
              <div className="empty-icon">◈</div>
              <div>Enter a topic above to start the multi-agent discussion</div>
              <div className="empty-sub">
                {rounds === 1 ? "1 round" : `${rounds} rounds`} · 6 AI agents will debate and synthesize the best idea
              </div>
              <div className="empty-agents-preview">
                {["◈ Nova", "✦ Spark", "⬡ Axiom", "◎ Empathy", "⬟ Vex", "◉ Weave"].map((a) => (
                  <span key={a} className="empty-agent-tag">{a}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
