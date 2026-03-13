@echo off
setlocal EnableDelayedExpansion
title ApplyBot Installer

echo ============================================
echo  ApplyBot Installer
echo ============================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not on PATH.
    echo Download Python 3.9+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Check Python version is 3.9+
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set PYMAJ=%%a
    set PYMIN=%%b
)
if !PYMAJ! LSS 3 (
    echo ERROR: Python 3.9 or higher is required. Found !PYVER!
    pause
    exit /b 1
)
if !PYMAJ! EQU 3 if !PYMIN! LSS 9 (
    echo ERROR: Python 3.9 or higher is required. Found !PYVER!
    pause
    exit /b 1
)

echo Python !PYVER! found. OK.
echo.

:: Install base applybot
echo Installing ApplyBot...
pip install --upgrade applybot
if errorlevel 1 (
    echo ERROR: pip install failed. Check your internet connection and try again.
    pause
    exit /b 1
)
echo.

:: Ask about browser automation
set /p BROWSER="Enable browser auto-apply? (LinkedIn, Greenhouse, Lever) [y/N]: "
if /i "!BROWSER!"=="y" (
    echo Installing Playwright...
    pip install "applybot[browser]"
    if errorlevel 1 (
        echo ERROR: Failed to install browser extras.
        pause
        exit /b 1
    )
    echo Installing Chrome browser for Playwright...
    playwright install chrome
    if errorlevel 1 (
        echo ERROR: playwright install chrome failed.
        echo Ensure Google Chrome is installed, then run: playwright install chrome
        pause
        exit /b 1
    )
    echo Browser automation enabled.
    echo.
    echo Next: run  applybot login linkedin  to save your LinkedIn session.
    echo.
)

echo ============================================
echo  ApplyBot installed successfully!
echo ============================================
echo.
echo Get started:
echo   applybot init          -- run the setup wizard
echo   applybot run --dry-run -- test without submitting
echo   applybot run           -- go live
echo.
pause
