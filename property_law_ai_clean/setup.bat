@echo off
echo ===================================================
echo Property Law AI Assistant - Setup Script
echo ===================================================
echo.

echo Step 1: Creating virtual environment...
cd backend
python -m venv venv
echo Virtual environment created!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo Virtual environment activated!
echo.

echo Step 3: Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed!
echo.

echo Step 4: Setup complete!
echo.
echo ===================================================
echo NEXT STEPS:
echo ===================================================
echo.
echo 1. Get your API keys:
echo    - OpenAI API key from: https://platform.openai.com/api-keys
echo    - Supabase project from: https://supabase.com
echo.
echo 2. Edit backend\.env file with your API keys
echo.
echo 3. Run start.bat to launch the application
echo.
echo ===================================================
pause