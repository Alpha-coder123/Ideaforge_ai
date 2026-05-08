const AGENTS = [
  { id: "strategist", name: "Nova",    role: "Strategic Thinker",  color: "#00FFD1", avatar: "◈" },
  { id: "creative",   name: "Spark",   role: "Creative Disruptor", color: "#FF6B6B", avatar: "✦" },
  { id: "technical",  name: "Axiom",   role: "Technical Architect",color: "#7B68EE", avatar: "⬡" },
  { id: "empathy",    name: "Empathy", role: "User Advocate",      color: "#FFC107", avatar: "◎" },
  { id: "critic",     name: "Vex",     role: "Devil's Advocate",   color: "#FF4757", avatar: "⬟" },
  { id: "synthesizer",name: "Weave",   role: "Idea Synthesizer",   color: "#26de81", avatar: "◉" },
];

export default function AgentStrip() {
  return (
    <div className="agents-strip">
      {AGENTS.map((a) => (
        <div
          key={a.id}
          className="agent-chip"
          style={{ "--chip-color": a.color }}
        >
          <span style={{ color: a.color, fontSize: 14 }}>{a.avatar}</span>
          <span className="chip-name" style={{ color: a.color }}>
            {a.name}
          </span>
          <span className="chip-role">· {a.role}</span>
        </div>
      ))}
    </div>
  );
}
