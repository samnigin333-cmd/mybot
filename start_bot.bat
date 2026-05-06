@echo off
title Korporativ Bot
color 0A
echo ============================================
echo   KORPORATIV BOT ISHGA TUSHMOQDA...
echo ============================================
echo.
cd /d "%~dp0"
pip install -r requirements.txt -q
echo Bot ishga tushdi! Bu oynani yopmang.
echo Botni toxtatish uchun: Ctrl+C
echo ============================================
python bot.py
pause