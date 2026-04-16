@echo off
title Color Picker - Khoi dong
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================
echo    COLOR PICKER - STARTING
echo ==========================================

:: 1. Kiem tra Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
    echo [OK] Da tim thay: !PY_VER!
) else (
    echo [THONG BAO] Khong tim thay Python tren may.
    echo Dang thu cai dat Python 3.13 bang winget...
    
    winget install Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    
    if %errorlevel% neq 0 (
        echo [THU LAI] winget khong san sang, dang thu tai bang curl.exe...
        echo Vui long doi trong giay lat...
        
        rem Tai installer bang curl.exe
        echo Dang tai tu: https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe
        curl.exe -L "https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe" -o python_installer.exe
        
        if %errorlevel% neq 0 (
            echo [THU LAI] curl that bai, dang thu bang PowerShell...
            powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe' -OutFile 'python_installer.exe' -UseBasicParsing"
        )
        
        if exist python_installer.exe (
            echo Dang cai dat thầm lặng...
            start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
            del python_installer.exe
        )
    )
    
    rem Kiem tra lai sau khi thu moi cach
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [LOI] Khong the cai dat Python tu dong. 
        echo Vui long tai va cai dat thu cong tai: https://www.python.org/downloads/
        pause
        exit /b
    )
    
    echo [XONG] Da xac nhan Python. 
    echo Neu buoc tiep theo bao loi, vui long tat cua so nay va chay lai Install.bat nhe!
    timeout /t 3 >nul
)

:: 2. Thiet lap moi truong ao (venv) neu chua co
if not exist .venv (
    echo Dang khoi tao moi truong ao ^(chi thuc hien lan dau^)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [LOI] Khong the tao venv. Hay dam bao ban co quyen ghi vao thu muc nay.
        pause
        exit /b
    )
    
    echo Dang cai dat cac thu vien can thiet ^(Pillow, CustomTkinter, NumPy^)...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [LOI] Khong the cai dat thu vien. Kiem tra ket noi mang.
        pause
        exit /b
    )
)

echo [THANH CONG] Da cai xong cac thu vien can thiet.
pause
exit /b 0
