@echo off
REM ===========================================================
REM  Kick auto drops - launcher
REM  Keeps the console window open so you can read output/errors
REM  even if you start it by double-click.
REM ===========================================================
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py index.py
) else (
    python index.py
)

echo.
echo ===========================================================
echo  Program finished. Press any key to close this window.
echo ===========================================================
pause >nul
