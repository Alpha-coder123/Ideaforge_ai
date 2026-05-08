# IdeaForge 🔮
## AI Multi-Agent Ideation Platform
### Fully Local · No Cloud AI APIs · HuggingFace Transformers + FastAPI + React

---

## What It Does

IdeaForge runs **6 specialized AI agents** entirely on your own machine — no OpenAI, no Gemini, no external API calls. You give it a topic or idea thread, and the agents debate it across multiple rounds, each building on what the others said. At the end, a synthesis step produces a structured **best version of your idea** as the final output.

```
Your Idea Thread
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  Round 1 → Round 2 → Round N (1–3 rounds)           │
│                                                     │
│  ◈ Nova      → Strategic angle                      │
│  ✦ Spark     → Creative / disruptive angle          │
│  ⬡ Axiom     → Technical feasibility                │
│  ◎ Empathy   → User needs & UX                      │
│  ⬟ Vex       → Devil's advocate / risks             │
│  ◉ Weave     → Synthesis of prior messages          │
└─────────────────────────────────────────────────────┘
      │
      ▼
Final Synthesized Idea (structured output)
```

**Key goals:**
- Save time that would otherwise be spent in real team discussions
- Bring multiple expert perspectives (strategy, tech, UX, criticism) to every idea
- Produce a refined, actionable version of your original thread

---

## The 6 Agents

| Avatar | Name | Role | Focus |
|--------|------|------|-------|
| ◈ | **Nova** | Strategic Thinker | Market fit, business viability, long-term vision |
| ✦ | **Spark** | Creative Disruptor | Bold angles, unconventional approaches |
| ⬡ | **Axiom** | Technical Architect | Feasibility, tech stack, MVP scope |
| ◎ | **Empathy** | User Advocate | Pain points, UX, adoption barriers |
| ⬟ | **Vex** | Devil's Advocate | Risks, weaknesses, stress-testing |
| ◉ | **Weave** | Idea Synthesizer | Pulls all threads into a refined concept |

Each agent receives the full discussion history, so later agents can agree, disagree, or build on earlier responses.

---

## Project Structure

```
ideaforge/
├── backend/
│   ├── main.py              ← FastAPI server + SSE streaming endpoints
│   ├── model_manager.py     ← HuggingFace model loading, device detection, inference
│   ├── agents.py            ← Agent personas + prompt builders (per model family)
│   ├── orchestrator.py      ← Multi-agent discussion loop, history management
│   └── requirements.txt     ← Python dependencies
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.jsx
        ├── App.jsx                   ← Root component, SSE client, state management
        ├── styles/globals.css
        └── components/
            ├── ModelLoader.jsx       ← Model selection UI (first-load + mid-session switcher)
            ├── AgentStrip.jsx        ← Agent chip row
            ├── ThreadInput.jsx       ← Topic input + round selector + run button
            ├── DiscussionFeed.jsx    ← Live scrolling feed
            ├── MessageBubble.jsx     ← Individual agent message card
            ├── ProgressBar.jsx       ← Progress indicator
            └── FinalOutput.jsx       ← Synthesized result display
```

---

## Requirements

| | Minimum | Recommended |
|---|---|---|
| **Python** | 3.9 | 3.11 |
| **Node.js** | 16 | 18+ |
| **RAM** | 2 GB (flan-t5-base) | 8+ GB |
| **GPU** | Not required | NVIDIA GPU speeds up larger models significantly |
| **Disk** | 500 MB (flan-t5-base cached) | 10 GB for multiple models |

> **Important:** IdeaForge uses **only locally downloaded HuggingFace models**. It does not call ChatGPT, Gemini, Claude, or any external AI API. Your data stays on your machine.

---

## Setup & Installation

### Step 1 — Get the project

```bash
# Unzip or clone the project, then enter the directory
cd ideaforge
```

### Step 2 — Set up the Python backend

```bash
cd backend

# Create a virtual environment (strongly recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **PyTorch note:** The `requirements.txt` installs the CPU-only version of PyTorch which works everywhere.
> If you have an NVIDIA GPU, get the CUDA-enabled wheel from https://pytorch.org/get-started/locally/ for much faster inference.

### Step 3 — Start the backend server

```bash
# Make sure your virtualenv is still active
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 4 — Set up and start the frontend (new terminal window)

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

### Step 5 — Open the app

Go to **http://localhost:5173** in your browser.

### Step 6 — Load a model

When the app opens, you'll see the **Load a Local Model** screen. Pick a model (see table below), click **Load**, and wait for it to download and initialize. This only happens once per model — it's cached at `~/.cache/huggingface/hub/` for all future sessions.

---

## Model Selection Guide

| Model ID | Label | Download | RAM | Speed | Best For |
|----------|-------|----------|-----|-------|----------|
| `google/flan-t5-base` | Flan-T5 Base | ~250 MB | ~1 GB | ⚡ Fast | Testing, low-spec machines |
| `google/flan-t5-large` | Flan-T5 Large | ~780 MB | ~2 GB | ⚡ Fast | Most laptops |
| `google/flan-t5-xl` | Flan-T5 XL | ~3 GB | ~5 GB | ◑ Moderate | Better quality seq2seq |
| `Qwen/Qwen2-0.5B-Instruct` | Qwen2 0.5B | ~1 GB | ~2 GB | ⚡ Fast | Great tiny chat model |
| `Qwen/Qwen2-1.5B-Instruct` | Qwen2 1.5B | ~3 GB | ~4 GB | ◑ Moderate | Good quality + speed |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | TinyLlama | ~2.2 GB | ~3 GB | ◑ Moderate | Conversational quality |
| `microsoft/phi-2` | Phi-2 | ~5.5 GB | ~6 GB | ◔ Slow CPU | High reasoning quality |

> **First run recommendation:** Start with `google/flan-t5-base` to verify everything works, then switch to a larger model for better quality.

### Switching Models Mid-Session

After loading, a **Switch Model** button appears next to the model badge in the header. Click it to open the model switcher panel without losing your current session state. The old model is unloaded from RAM before the new one loads.

---

## How It Works

### Backend — FastAPI + SSE Streaming

The backend exposes these main endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check model status |
| `/api/load-model?model_name=...` | POST | Load / swap a model |
| `/api/unload-model` | POST | Free RAM |
| `/api/discuss` | POST | Run discussion (streams SSE events) |
| `/api/agents` | GET | List all agent definitions |

The `/api/discuss` endpoint streams **Server-Sent Events** so the frontend updates in real time as each agent finishes thinking.

### Agent Orchestration Loop

```python
for round in range(1, rounds + 1):      # 1–3 rounds
    for agent in selected_agents:        # 6 agents
        prompt = build_prompt(            # persona-aware prompt
            agent, thread, history, round, model_name
        )
        response = model.generate(prompt)
        yield SSE_event("agent_message", response)
        history.append(response)         # each agent sees all prior messages

synthesis = model.generate(synthesis_prompt(history))
yield SSE_event("synthesis_done", synthesis)
```

### Prompt Strategy

Prompts automatically adapt to the model architecture:

| Model Family | Prompt Format |
|---|---|
| `flan-t5`, `t5` | Instruction-completion (seq2seq style) |
| `phi-2` | `Instruct: … Output:` format |
| `TinyLlama`, `Mistral`, `LLaMA` | `<\|system\|>…<\|user\|>…<\|assistant\|>` chat format |
| `Qwen2` + others | `### System / ### Task / ### Response` format |

### Frontend — React + Vite

- Native **Fetch + ReadableStream** API consumes the SSE stream (no EventSource — allows POST with body)
- Events parsed line-by-line, UI updates live
- Typing indicators show while the model is generating
- Auto-scroll to the latest message

---

## Configuration

### Discussion rounds

In the UI: 1, 2, or 3 rounds (selector in the input bar).
Hard cap in `backend/main.py`:
```python
rounds=min(max(request.rounds, 1), 3)
```

### Generation quality

Edit `backend/model_manager.py` — `pipeline(...)` arguments:
```python
temperature=0.8,           # 0.0 = deterministic, 1.0 = very creative
top_p=0.92,                # nucleus sampling threshold
repetition_penalty=1.3,    # higher = less repetition
no_repeat_ngram_size=3,    # blocks 3-word repeat phrases
```

Edit `backend/orchestrator.py` — token budgets:
```python
400    # max_new_tokens per agent response
600    # max_new_tokens for the final synthesis
```

---

## Troubleshooting

**Backend won't start / import errors**
→ Make sure your virtualenv is activated before running `uvicorn`
→ Run `pip install -r requirements.txt` again

**Model download is slow / times out**
→ HuggingFace downloads can be slow. The download resumes if interrupted — just run the load again
→ You can pre-download manually: `huggingface-cli download google/flan-t5-base`

**Out of memory / model crashes**
→ Use a smaller model (`flan-t5-base` uses ~1 GB)
→ Close other apps to free RAM
→ Restart the backend server to clear leaked memory

**`CUDA out of memory`**
→ Uncomment `bitsandbytes` in `requirements.txt` and reinstall — this enables 4-bit quantization
→ Or use a smaller model

**Responses are too short / low quality**
→ Use a larger model (flan-t5-large, Qwen2-1.5B, or TinyLlama)
→ Increase `max_new_tokens` in `orchestrator.py`

**Frontend shows "Model not loaded" after refreshing**
→ The model stays loaded as long as the backend is running. If you restart uvicorn, reload the model via the UI

**Frontend can't connect to backend**
→ Verify uvicorn is running on port 8000
→ Check the browser console for CORS errors — ensure you're accessing the app at `localhost:5173` not `127.0.0.1:5173`

---

## Extending the Project

- **Add a new agent** → Add an entry to the `AGENTS` list in `backend/agents.py`
- **Change a persona** → Edit the `persona` or `personality` field for any agent
- **Add model support** → Add a new branch in `build_prompt()` in `agents.py` matching the new model's format
- **Persist discussions** → Add SQLite via SQLAlchemy in the backend, store `history` per session
- **Export to Markdown/PDF** → Add an export button in `FinalOutput.jsx` and a `/api/export` endpoint
- **Agent voting round** → Add a post-synthesis pass where agents vote on the best idea
- **Selective agents** → The backend already supports `selected_agents: list[str]` in the request body — wire it to a checkbox UI in `AgentStrip.jsx`

---

## Privacy

All model inference runs locally on your machine. No prompts, threads, or generated text are sent to any external service. The only network requests are:
1. Downloading model weights from HuggingFace Hub on first use (cached locally after)
2. Your browser talking to `localhost:8000` (your own machine)
