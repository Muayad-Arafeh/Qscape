@echo off
cd /d %~dp0\backend
echo Starting Qscape Backend on port 8000...
..\qscape_env\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if errorlevel 1 (
    echo Error starting backend. Make sure port 8000 is not in use.
    pause
)
