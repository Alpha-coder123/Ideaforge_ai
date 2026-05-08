import { useEffect, useRef } from "react";
import { MessageBubble, TypingIndicator } from "./MessageBubble";

export default function DiscussionFeed({ messages, currentTyping }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentTyping]);

  return (
    <div className="feed-section">
      <div className="section-header">
        <span className="section-label">Agent Discussion</span>
        <div className="section-line" />
        <span className="msg-count">{messages.length} messages</span>
      </div>

      <div className="discussion-feed">
        {messages.map((msg, i) => {
          const showDivider =
            i > 0 && msg.round !== messages[i - 1].round;
          return (
            <div key={msg.id}>
              {showDivider && (
                <div className="round-divider">
                  <div className="round-line" />
                  <span>Round {msg.round}</span>
                  <div className="round-line" />
                </div>
              )}
              <MessageBubble message={msg} />
            </div>
          );
        })}

        {currentTyping && <TypingIndicator agent={currentTyping} />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
