@echo off
REM FitBuddy - simple start script for Windows
cd /d "%~dp0"

if exist fitbuddy-env\Scripts\activate.bat (
    echo Activating virtual environment...
    call fitbuddy-env\Scripts\activate.bat
) else (
    echo Virtual environment "fitbuddy-env" not found.
    echo Create it first with:  python -m venv fitbuddy-env
    echo Then run:  pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist .env (
    echo WARNING: .env file not found. Copy .env.example to .env and add your Gemini API key.
)

echo Starting FitBuddy at http://127.0.0.1:8000
python -m uvicorn app.main:app --reload
pause
