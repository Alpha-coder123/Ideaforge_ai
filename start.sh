#!/bin/bash
# IdeaForge — Quick Start Script (macOS / Linux)
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        IdeaForge — Starting Up           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Backend ─────────────────────────────────────────────────
echo "▶ Setting up Python backend..."
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "  Installing Python dependencies..."
pip install -r requirements.txt -q

echo "  Starting backend on http://localhost:8000 ..."
uvicorn main:app --port 8000 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# ── Frontend ─────────────────────────────────────────────────
cd ../frontend
echo ""
echo "▶ Setting up frontend..."

if [ ! -d "node_modules" ]; then
  echo "  Installing npm packages..."
  npm install
fi

echo "  Starting frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅  IdeaForge is running!               ║"
echo "║  Open: http://localhost:5173             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait and clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
