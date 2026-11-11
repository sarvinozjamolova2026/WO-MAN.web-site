@echo off
title WO&MAN Barbershop — Dynamic Server
cd /d "%~dp0"

echo ===============================================================
echo   WO^&MAN BARBERSHOP — SERVER VA DASTURNI ISHGA TUSHIRISH
echo ===============================================================
echo.
echo 1. Server ishga tushirilmoqda...
echo 2. Sayt brauzeringizda avtomatik ochiladi: http://127.0.0.1:5000
echo.
echo Admin paneli:     http://127.0.0.1:5000/login (admin / Admin2026!WM)
echo Barber kabineti:  http://127.0.0.1:5000/login (pro_akrom, pro_axror, pro_jamoliddin / Pro2026!WM)
echo.
echo Serverni to'xtatish uchun: ushbu oynani yoping yoki Ctrl+C bosing.
echo ===============================================================
echo.

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"
call ".\venv\Scripts\python.exe" run.py

pause
