@echo off
REM Builds dist\GoneFishin.exe from the Python source.

REM Run from this script's folder, even if launched from somewhere else.
cd /d "%~dp0"

echo Installing requirements...
python -m pip install -r requirements.txt || goto :error

REM --onefile   bundle everything into a single .exe
REM --windowed  don't open a console window behind the game
echo Building GoneFishin.exe...
python -m PyInstaller --onefile --windowed --noconfirm --name GoneFishin main.py || goto :error

echo.
echo Done! The executable is at dist\GoneFishin.exe
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
