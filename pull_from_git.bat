@echo off
REM ============================================
REM Auto Pull from GitHub Script
REM ============================================
chcp 65001 >nul
color 0B

echo.
echo ╔════════════════════════════════════════╗
echo ║   Color Picker - Auto Pull from GitHub ║
echo ╚════════════════════════════════════════╝
echo.

REM Kiểm tra xem có trong folder Git repo không
if not exist .git (
    echo ❌ Lỗi: Không tìm thấy .git folder!
    echo Hãy chạy script này trong folder dự án.
    pause
    exit /b 1
)

REM Hiển thị status hiện tại
echo 📊 Trạng thái hiện tại:
echo.
git status
echo.

REM Hỏi xác nhận
set /p confirm="Bạn có muốn pull code mới nhất từ GitHub? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo ⚠️  Đã hủy.
    pause
    exit /b 0
)

REM Fetch
echo.
echo 📍 Đang fetch từ remote...
git fetch origin
if errorlevel 1 (
    echo ❌ Lỗi khi fetch!
    pause
    exit /b 1
)
echo ✅ Fetch thành công

REM Pull
echo.
echo 🔄 Đang pull code từ GitHub...
git pull origin main
if errorlevel 1 (
    echo ❌ Lỗi khi pull!
    echo.
    echo Các lý do có thể xảy ra:
    echo  1. Có conflict với file local
    echo  2. Branch tên không phải "main"
    echo.
    pause
    exit /b 1
)
echo ✅ Pull thành công!

echo.
echo ╔════════════════════════════════════════╗
echo ║   ✨ Code đã cập nhật! ✨              ║
echo ║   Bạn có thể xem code mới nhất          ║
echo ╚════════════════════════════════════════╝
echo.
pause
