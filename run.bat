@echo off
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error. Press any key to close...
    pause >nul
)
