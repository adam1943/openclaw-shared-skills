@echo off
echo =====================================
echo   OpenClaw Gateway Service Install
echo =====================================
echo.
echo Stopping existing Gateway...
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo Installing Gateway as Windows Service...
openclaw gateway install --force

echo.
echo Starting Gateway Service...
openclaw gateway start

echo.
echo Waiting for service to start...
timeout /t 3 /nobreak >nul

echo.
echo Checking service status...
openclaw gateway status

echo.
echo =====================================
echo Installation Complete!
echo =====================================
echo.
pause
