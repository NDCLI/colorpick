@echo off
title Setup Color Picker Suite
setlocal enabledelayedexpansion

:: Cấu hình đường dẫn và URL
set GITHUB_RELEASE_URL=https://github.com/NDCLI/colorpick/releases/latest/download
set GITHUB_RAW_URL=https://raw.githubusercontent.com/NDCLI/colorpick/master
set INSTALL_DIR=%USERPROFILE%\Documents\ColorPickerSuite
set APP_FILE=ColorPicker.pyw
set REQ_FILE=requirements.txt

echo ======================================================
echo    COLOR PICKER SUITE - AUTO SETUP (Documents)
echo ======================================================

:: 0. Tạo thư mục cài đặt
if not exist "%INSTALL_DIR%" (
    echo [0/4] Dang tao thu muc tai: %INSTALL_DIR%
    mkdir "%INSTALL_DIR%"
)
cd /d "%INSTALL_DIR%"

:: 1. Kiem tra va cai dat Python 3.13 tu Microsoft Store (qua winget)
echo [1/4] Kiem tra Python 3.13...
py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Khong tim thay Python 3.13. Dang cai dat tu Microsoft Store...
    winget install Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
    
    :: Thử làm mới PATH cho phiên làm việc hiện tại (tạm thời)
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts"
    
    py -3.13 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Canh bao: winget vua chay xong nhung python chua nhan ngay.
        echo Vui long tat cua so nay va chay lai script mot lan nua de hoan tat.
        pause
        exit /b
    )
    echo [OK] Da cai dat Python 3.13.
) else (
    echo [OK] Python 3.13 da san sang.
)

:: 2. Tải File ứng dụng và requirements
echo [2/4] Dang tai phien ban MOI NHAT tu GitHub Releases...
curl -L -O %GITHUB_RELEASE_URL%/%APP_FILE%
curl -L -O %GITHUB_RAW_URL%/%REQ_FILE%

if not exist "%APP_FILE%" (
    echo [LOI] Khong the tai file. Kiem tra ket noi mang.
    pause
    exit /b
)
echo [OK] Da tai xong cac file can thiet.

:: 3. Cài đặt thư viện
echo [3/4] Dang cai dat thu vien Python...
py -3.13 -m pip install --upgrade pip
py -3.13 -m pip install -r %REQ_FILE%

:: 4. Tạo Shortcut ngoài Desktop (PowerShell)
echo [4/4] Dang tao shortcut ngoai Desktop...
set SCRIPT_PATH=%INSTALL_DIR%\%APP_FILE%
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Color Picker.lnk
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = 'pyw.exe'; $Shortcut.Arguments = '-3.13 \"%SCRIPT_PATH%\"'; $Shortcut.Save()"

echo ======================================================
echo [THANH CONG] Setup hoan tat!
echo 1. Ung dung da duoc cai vao: Documents\ColorPickerSuite
echo 2. Da co icon "Color Picker" ngoai Desktop.
echo ======================================================
pause
start py -3.13w "%APP_FILE%"
exit /b

