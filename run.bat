@echo off
cd /d "%~dp0"
start "BrandPulse Backend" cmd /k "cd /d backend && run.bat"
timeout /t 3 /nobreak >nul
start "BrandPulse Frontend" http://127.0.0.1:5500/index.html
python -m http.server 5500 --bind 127.0.0.1
