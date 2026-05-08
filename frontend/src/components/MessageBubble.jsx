import { useEffect, useState } from "react";

export function TypingIndicator({ agent }) {
  if (!agent) return null;
  return (
    <div
      className="typing-indicator"
      style={{ "--agent-color": agent.color }}
    >
      <span style={{ color: agent.color, fontSize: 16 }}>{agent.avatar}</span>
      <span className="agent-name" style={{ color: agent.color }}>
        {agent.name}
      </span>
      <span className="agent-role-small">{agent.role}</span>
      <span className="dots">
        <span>.</span>
        <span>.</span>
        <span>.</span>
      </span>
    </div>
  );
}

export function MessageBubble({ message }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      className={`message-bubble ${visible ? "visible" : ""}`}
      style={{ "--agent-color": message.agentColor }}
    >
      <div className="message-header">
        <span style={{ color: message.agentColor, fontSize: 16 }}>
          {message.agentAvatar}
        </span>
        <span className="msg-name" style={{ color: message.agentColor }}>
          {message.agentName}
        </span>
        <span className="msg-role">{message.agentRole}</span>
        <span className="msg-round">Round {message.round}</span>
      </div>
      <div className="message-content">{message.content}</div>
    </div>
  );
}
