"""
DiscussionOrchestrator — Manages the multi-agent discussion loop.
Runs agents sequentially, builds context, streams SSE events to the frontend.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from agents import AGENTS, AGENTS_BY_ID, build_prompt, build_synthesis_prompt
from model_manager import ModelManager

logger = logging.getLogger(__name__)


class DiscussionOrchestrator:
    def __init__(
        self,
        model_manager: ModelManager,
        thread: str,
        rounds: int = 2,
        selected_agents: Optional[list[str]] = None,
    ):
        self.model_manager = model_manager
        self.thread = thread
        self.rounds = rounds
        self.history: list[dict] = []

        # Filter agents if specific ones are requested
        if selected_agents:
            self.agents = [a for a in AGENTS if a["id"] in selected_agents]
        else:
            self.agents = AGENTS

        if not self.agents:
            self.agents = AGENTS  # fallback to all

    async def run(self) -> AsyncGenerator[dict, None]:
        """Main discussion loop — yields SSE event dicts."""

        total_steps = len(self.agents) * self.rounds + 1
        step = 0

        yield {
            "type": "discussion_start",
            "thread": self.thread,
            "total_steps": total_steps
        }

        for round_num in range(1, self.rounds + 1):
            yield {"type": "round_start", "round": round_num}

            for agent in self.agents:
                yield {
                    "type": "agent_start",
                    "agentId": agent["id"],
                    "agentName": agent["name"],
                    "agentRole": agent["role"],
                    "agentColor": agent["color"],
                    "agentAvatar": agent["avatar"],
                    "round": round_num,
                }

                # Build prompt
                prompt = await asyncio.to_thread(
                    build_prompt,
                    agent,
                    self.thread,
                    self.history,
                    round_num,
                    self.model_manager.model_name,
                )

                logger.info(f"[Round {round_num}] {agent['name']} generating...")

                # Run inference in thread pool (CPU-bound, must not block event loop)
                response = await asyncio.to_thread(
                    self.model_manager.generate,
                    prompt,
                    400,   # max tokens per agent response
                )

                # Clean the response
                response = self._clean_response(response, agent["name"])

                # Save to history so next agents can reference it
                msg = {
                    "agentId": agent["id"],
                    "agentName": agent["name"],
                    "agentRole": agent["role"],
                    "agentColor": agent["color"],
                    "agentAvatar": agent["avatar"],
                    "content": response,
                    "round": round_num,
                }
                self.history.append(msg)

                step += 1
                progress = int((step / total_steps) * 88)

                yield {
                    "type": "agent_message",
                    **msg,
                    "progress": progress,
                }

                # Small yield to let event loop breathe
                await asyncio.sleep(0.05)

            yield {"type": "round_end", "round": round_num}

        # ── Synthesis Phase ───────────────────────────────────────────────────
        yield {"type": "synthesis_start"}

        synthesis_prompt = await asyncio.to_thread(
            build_synthesis_prompt,
            self.thread,
            self.history,
            self.model_manager.model_name,
        )

        logger.info("Generating final synthesis...")

        # Give synthesis more tokens for a complete output
        synthesis = await asyncio.to_thread(
            self.model_manager.generate,
            synthesis_prompt,
            600,   # more tokens for the final synthesis
        )

        synthesis = self._clean_synthesis(synthesis)

        yield {
            "type": "synthesis_done",
            "content": synthesis,
            "progress": 100,
        }

        yield {"type": "discussion_complete"}

    def _clean_response(self, text: str, agent_name: str) -> str:
        """Remove prompt artifacts and clean up generated text."""

        # Common artifacts to strip
        artifacts = [
            "Output:", "Response:", "Assistant:", "### Response",
            "<|assistant|>", "</s>", "<s>", "Instruct:", "### Instruction",
            f"{agent_name}:", "Output:\n", "Response:\n",
            "Give a thorough response", "Give a detailed response",
            "Write at least", "provide a detailed analysis",
        ]
        for artifact in artifacts:
            if text.startswith(artifact):
                text = text[len(artifact):].strip()

        text = text.strip()

        # Remove incomplete last sentence (ends mid-word)
        if len(text) > 50 and not text[-1] in ".!?":
            last_period = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
            if last_period > len(text) * 0.5:
                text = text[:last_period + 1]

        # Fallback for very short responses
        if len(text) < 30:
            text = (
                f"From the {agent_name} perspective: This idea has significant potential "
                f"and deserves careful consideration from multiple angles. "
                f"Further analysis of the core concept would strengthen the overall approach."
            )

        return text

    def _clean_synthesis(self, text: str) -> str:
        """Clean and format the synthesis output."""

        # Strip common artifacts
        artifacts = [
            "Output:", "Response:", "Assistant:", "### Response",
            "<|assistant|>", "</s>", "<s>",
        ]
        for artifact in artifacts:
            if text.startswith(artifact):
                text = text[len(artifact):].strip()

        text = text.strip()

        # If synthesis is too short, build a fallback from agent history
        if len(text) < 80:
            text = self._build_fallback_synthesis()

        return text

    def _build_fallback_synthesis(self) -> str:
        """
        Build a structured synthesis manually from agent history
        when the model produces a too-short output.
        """
        lines = [
            f"SYNTHESIZED IDEA FOR: {self.thread}\n",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        ]

        lines.append("KEY INSIGHTS FROM EACH EXPERT:\n")
        for msg in self.history:
            lines.append(f"\n{msg['agentName']} ({msg['agentRole']}) — Round {msg['round']}:")
            lines.append(f"{msg['content']}\n")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("\nRECOMMENDED NEXT STEPS:")
        lines.append("1. Validate the core concept with real users through interviews or surveys.")
        lines.append("2. Build a minimal prototype focusing on the single most valuable feature.")
        lines.append("3. Address the key risks identified during the discussion before scaling.")

        return "\n".join(lines)
