@echo off
cd /d %~dp0\frontend
echo Starting Qscape Frontend on port 8080...
..\qscape_env\Scripts\python.exe -m http.server 8080
if errorlevel 1 (
    echo Error starting frontend. Make sure port 8080 is not in use.
    pause
)
