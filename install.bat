@echo off
title Bot O'rnatish
color 0B
echo ============================================
echo   BOT O'RNATILMOQDA...
echo ============================================

cd /d "%~dp0"

:: Desktop shortcut yaratish
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Korporativ Bot.lnk
set TARGET=%~dp0start_bot.bat
set ICON=%SystemRoot%\System32\shell32.dll

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Korporativ Bot'; $s.Save()"

echo.
echo ✅ O'rnatish tugadi!
echo.
echo Desktop'ingizda "Korporativ Bot" yorlig'i yaratildi.
echo Botni ishga tushirish uchun shu yorliqni ikki marta bosing.
echo.
pause
