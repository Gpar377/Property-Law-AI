@echo off
echo ===================================================
echo Property Law AI Assistant - Starting Both Servers
echo ===================================================
echo.

echo Starting Backend Server (Port 8001)...
start "Backend Server" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && echo Backend running at http://localhost:8001 && uvicorn main:app --reload --host 0.0.0.0 --port 8001"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server (Port 3000)...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && echo Frontend running at http://localhost:3000 && python serve.py"

echo.
echo Both servers are starting...
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo.
echo Opening frontend in browser...
timeout /t 3 /nobreak > nul
start "" "http://localhost:3000"

echo.
echo Both servers are now running in separate windows.
echo Close this window when done.
pause