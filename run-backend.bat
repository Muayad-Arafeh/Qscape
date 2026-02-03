@echo off
cd /d %~dp0\backend
echo Starting Qscape Backend on port 9000...
..\qscape_env\Scripts\python.exe -m daphne -b 0.0.0.0 -p 9000 main:app
if errorlevel 1 (
    echo Error starting backend. Make sure port 9000 is not in use.
    pause
)
