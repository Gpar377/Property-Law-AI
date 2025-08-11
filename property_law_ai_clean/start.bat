@echo off
echo ===================================================
echo Property Law AI Assistant - Starting Backend
echo ===================================================
echo.

echo Starting backend server...
cd backend
call venv\Scripts\activate

echo.
echo Backend server starting at: http://localhost:8000
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo IMPORTANT: Start the frontend separately using start_frontend.bat
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000