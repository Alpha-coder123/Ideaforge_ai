@echo off
echo.
echo ==========================================
echo        IdeaForge -- Starting Up
echo ==========================================
echo.

:: ── Backend ────────────────────────────────
echo [1/4] Setting up Python backend...
cd /d "%~dp0backend"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -r requirements.txt -q

echo Starting backend on http://localhost:8000 ...
start "IdeaForge Backend" cmd /k "venv\Scripts\activate.bat && uvicorn main:app --port 8000"

:: ── Frontend ───────────────────────────────
echo.
echo [2/4] Setting up frontend...
cd /d "%~dp0frontend"

if not exist node_modules (
    echo Installing npm packages...
    npm install
)

echo Starting frontend on http://localhost:5173 ...
start "IdeaForge Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo   IdeaForge is running!
echo   Open: http://localhost:5173
echo ==========================================
echo.
echo Close the two terminal windows to stop the servers.
pause
