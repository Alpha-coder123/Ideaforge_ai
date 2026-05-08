"""
Agent Definitions — Each agent has a unique persona, role, and prompt-building logic.
Prompts are carefully optimized to get detailed responses from small models like flan-t5-base.
"""

AGENTS = [
    {
        "id": "strategist",
        "name": "Nova",
        "role": "Strategic Thinker",
        "color": "#00FFD1",
        "avatar": "◈",
        "personality": "Analyzes market fit, business viability, and long-term vision.",
        "persona": "business strategy analyst who evaluates market opportunities",
    },
    {
        "id": "creative",
        "name": "Spark",
        "role": "Creative Disruptor",
        "color": "#FF6B6B",
        "avatar": "✦",
        "personality": "Challenges assumptions and finds unconventional, bold angles.",
        "persona": "creative innovation expert who finds unexpected and bold angles",
    },
    {
        "id": "technical",
        "name": "Axiom",
        "role": "Technical Architect",
        "color": "#7B68EE",
        "avatar": "⬡",
        "personality": "Evaluates feasibility, tech stack, and implementation paths.",
        "persona": "software architect who evaluates technical feasibility and implementation",
    },
    {
        "id": "empathy",
        "name": "Empathy",
        "role": "User Advocate",
        "color": "#FFC107",
        "avatar": "◎",
        "personality": "Champions user needs, pain points, and UX considerations.",
        "persona": "user experience researcher who focuses on human needs and adoption",
    },
    {
        "id": "critic",
        "name": "Vex",
        "role": "Devil's Advocate",
        "color": "#FF4757",
        "avatar": "⬟",
        "personality": "Stress-tests ideas, finds weaknesses, plays devil's advocate.",
        "persona": "critical analyst who identifies risks, flaws, and challenges",
    },
    {
        "id": "synthesizer",
        "name": "Weave",
        "role": "Idea Synthesizer",
        "color": "#26de81",
        "avatar": "◉",
        "personality": "Synthesizes all perspectives into refined, actionable ideas.",
        "persona": "synthesis expert who combines all perspectives into refined ideas",
    },
]

# Index for quick lookup
AGENTS_BY_ID = {a["id"]: a for a in AGENTS}


def build_prompt(agent: dict, thread: str, history: list[dict], round_num: int, model_name: str) -> str:
    """
    Build a strong, detailed prompt for each agent.
    Optimized to extract maximum quality from small models like flan-t5-base.
    """
    name = agent["name"]
    role = agent["role"]
    persona = agent["persona"]

    # Build context from previous messages (last 4 messages max to stay within token limits)
    context_lines = []
    if history:
        recent = history[-4:]
        for m in recent:
            short_content = m['content'][:300] if len(m['content']) > 300 else m['content']
            context_lines.append(f"{m['agentName']} said: {short_content}")
    context = "\n".join(context_lines)

    model_lower = model_name.lower()

    # ── flan-t5 / t5 style ────────────────────────────────────────────────────
    if "flan" in model_lower or "t5" in model_lower:
        if round_num == 1:
            if context:
                prompt = (
                    f"You are {name}, a {persona}. "
                    f"Analyze this idea from your expert perspective: {thread}\n\n"
                    f"Previous comments:\n{context}\n\n"
                    f"As {name} ({role}), provide a detailed analysis covering: "
                    f"1) Your main insight about this idea "
                    f"2) A specific recommendation "
                    f"3) One important consideration. "
                    f"Give a thorough response of at least 3 sentences:"
                )
            else:
                prompt = (
                    f"You are {name}, a {persona}. "
                    f"Analyze this idea thoroughly: {thread}\n\n"
                    f"As {name} ({role}), provide a detailed analysis covering: "
                    f"1) What makes this idea valuable or problematic "
                    f"2) A specific recommendation for improvement "
                    f"3) The most important factor to consider. "
                    f"Give a thorough response of at least 3 sentences:"
                )
        else:
            prompt = (
                f"You are {name}, a {persona}. "
                f"Topic being discussed: {thread}\n\n"
                f"What other experts said:\n{context}\n\n"
                f"As {name} ({role}), respond to the discussion by: "
                f"1) Agreeing or disagreeing with a specific point made above "
                f"2) Adding a new insight the others missed "
                f"3) Giving a concrete recommendation. "
                f"Give a detailed response of at least 3 sentences:"
            )

    # ── phi-2 style ───────────────────────────────────────────────────────────
    elif "phi" in model_lower:
        if context:
            prompt = (
                f"Instruct: You are {name}, a {persona}.\n"
                f"Topic: {thread}\n"
                f"Discussion so far:\n{context}\n\n"
                f"Task: As {name} ({role}), provide a detailed analysis with specific insights, "
                f"a concrete recommendation, and an important consideration. Write at least 4 sentences.\n\n"
                f"Output:"
            )
        else:
            prompt = (
                f"Instruct: You are {name}, a {persona}.\n"
                f"Topic: {thread}\n\n"
                f"Task: As {name} ({role}), provide a detailed analysis with specific insights, "
                f"a concrete recommendation, and an important consideration. Write at least 4 sentences.\n\n"
                f"Output:"
            )

    # ── TinyLlama / Mistral / LLaMA chat format ───────────────────────────────
    elif "tinyllama" in model_lower or "mistral" in model_lower or "llama" in model_lower:
        context_part = f"\nDiscussion so far:\n{context}\n" if context else ""
        prompt = (
            f"<|system|>\nYou are {name}, a {persona}. "
            f"Always give detailed, specific responses of at least 4 sentences.</s>\n"
            f"<|user|>\n"
            f"Topic: {thread}\n"
            f"{context_part}\n"
            f"As {name} ({role}), provide your detailed analysis. Include: "
            f"your main insight, a specific recommendation, and an important consideration.</s>\n"
            f"<|assistant|>\n"
        )

    # ── Generic fallback ──────────────────────────────────────────────────────
    else:
        context_part = f"Discussion so far:\n{context}\n\n" if context else ""
        prompt = (
            f"### System\nYou are {name}, a {persona}.\n\n"
            f"### Topic\n{thread}\n\n"
            f"{context_part}"
            f"### Task\nAs {name} ({role}), provide a detailed analysis with: "
            f"your main insight, a specific recommendation, and an important consideration. "
            f"Write at least 4 sentences.\n\n"
            f"### Response\n"
        )

    return prompt


def build_synthesis_prompt(thread: str, history: list[dict], model_name: str) -> str:
    """
    Build a strong synthesis prompt that forces the model to produce
    a structured, multi-part final output.
    """
    # Build a clean discussion summary
    discussion_lines = []
    for m in history:
        short = m['content'][:250] if len(m['content']) > 250 else m['content']
        discussion_lines.append(f"{m['agentName']} ({m['agentRole']}): {short}")
    discussion = "\n".join(discussion_lines)

    model_lower = model_name.lower()

    # ── flan-t5 style ─────────────────────────────────────────────────────────
    if "flan" in model_lower or "t5" in model_lower:
        prompt = (
            f"Multiple experts discussed this idea: {thread}\n\n"
            f"Here is what each expert said:\n{discussion}\n\n"
            f"Based on all expert opinions above, write a comprehensive synthesis that includes:\n"
            f"1. THE BEST IDEA: Combine the strongest points from all experts into one refined concept.\n"
            f"2. KEY STRENGTHS: List 3 strengths identified by the experts.\n"
            f"3. MAIN CHALLENGES: List 2 challenges or risks to address.\n"
            f"4. NEXT STEPS: Give 3 specific actions to take immediately.\n"
            f"5. SUCCESS MEASURE: Explain how to know if this idea is working.\n\n"
            f"Write a detailed, structured synthesis of at least 8 sentences:"
        )

    # ── phi-2 style ───────────────────────────────────────────────────────────
    elif "phi" in model_lower:
        prompt = (
            f"Instruct: You are a master idea synthesizer.\n"
            f"Topic: {thread}\n\n"
            f"Expert discussion:\n{discussion}\n\n"
            f"Task: Write a comprehensive synthesis covering:\n"
            f"1. THE BEST IDEA: One refined concept combining all expert insights\n"
            f"2. KEY STRENGTHS: 3 strengths from the discussion\n"
            f"3. MAIN CHALLENGES: 2 risks to address\n"
            f"4. NEXT STEPS: 3 specific immediate actions\n"
            f"5. SUCCESS MEASURE: How to measure success\n\n"
            f"Output a detailed synthesis of at least 8 sentences:\n\nOutput:"
        )

    # ── TinyLlama / Mistral / LLaMA chat format ───────────────────────────────
    elif "tinyllama" in model_lower or "mistral" in model_lower or "llama" in model_lower:
        prompt = (
            f"<|system|>\nYou are a master idea synthesizer. "
            f"Always produce detailed, structured, comprehensive outputs.</s>\n"
            f"<|user|>\n"
            f"Topic: {thread}\n\n"
            f"Expert discussion:\n{discussion}\n\n"
            f"Write a comprehensive synthesis with:\n"
            f"1. THE BEST IDEA\n2. KEY STRENGTHS (3 points)\n"
            f"3. MAIN CHALLENGES (2 points)\n4. NEXT STEPS (3 actions)\n"
            f"5. SUCCESS MEASURE\n\n"
            f"Write at least 8 sentences.</s>\n"
            f"<|assistant|>\n"
        )

    # ── Generic fallback ──────────────────────────────────────────────────────
    else:
        prompt = (
            f"### System\nYou are a master idea synthesizer.\n\n"
            f"### Topic\n{thread}\n\n"
            f"### Expert Discussion\n{discussion}\n\n"
            f"### Task\nWrite a comprehensive synthesis covering:\n"
            f"1. THE BEST IDEA: One refined concept combining all insights\n"
            f"2. KEY STRENGTHS: 3 strengths identified\n"
            f"3. MAIN CHALLENGES: 2 risks to address\n"
            f"4. NEXT STEPS: 3 specific immediate actions\n"
            f"5. SUCCESS MEASURE: How to measure success\n\n"
            f"Write at least 8 sentences.\n\n"
            f"### Response\n"
        )

    return prompt
