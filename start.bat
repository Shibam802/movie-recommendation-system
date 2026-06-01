@echo off
echo.
echo   CineMatch -- Movie Recommendation System
echo   -----------------------------------------
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install from https://python.org
    pause & exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True)"

echo.
echo Starting server at http://localhost:5000
echo.
cd backend && python app.py
pause
