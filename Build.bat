@echo off
echo ===========================================
echo   BUILDING COLOR PICKER (.EXE)
echo ===========================================
echo.
echo [*] Checking environment...
python -m pip install pyinstaller

echo [*] Building EXE... (This may take a minute)
python -m PyInstaller --noconfirm --onefile --windowed --icon "assets/app_icon.ico" --name "Color Picker" "ColorPicker.pyw"

if %errorlevel% == 0 (
    echo.
    echo ===========================================
    echo   SUCCESS! 
    echo ===========================================
    echo [i] Your EXE is ready in the 'dist' folder.
    echo [*] Cleaning up temporary files...
    rd /s /q "build"
    del /f /q "*.spec"
    echo [i] Clean up complete.
    echo.
) else (
    echo.
    echo [!] ERROR: Build failed.
)
echo.
pause
