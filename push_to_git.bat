@echo off
REM ============================================
REM Auto Push to GitHub Script
REM ============================================
chcp 65001 >nul
color 0A

echo.
echo ╔════════════════════════════════════════╗
echo ║   Color Picker - Auto Push to GitHub   ║
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
echo 📊 Trạng thái file hiện tại:
echo.
git status --short
echo.

REM Hỏi người dùng xác nhận
set /p confirm="Bạn có muốn push các file này lên GitHub? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo ⚠️  Đã hủy.
    pause
    exit /b 0
)

REM Hỏi lời nhắn commit
echo.
set /p message="Nhập lời nhắn commit (mặc định: 'Update code'): "
if "%message%"=="" set message=Update code

REM Stage tất cả file
echo.
echo 📝 Đang thêm file...
git add .
if errorlevel 1 (
    echo ❌ Lỗi khi add file!
    pause
    exit /b 1
)
echo ✅ Đã add file thành công

REM Commit
echo.
echo 💾 Đang commit...
git commit -m "%message%"
if errorlevel 1 (
    echo ⚠️  Không có file nào thay đổi hoặc lỗi commit
    pause
    exit /b 1
)
echo ✅ Đã commit thành công

REM Push
echo.
echo 🚀 Đang push lên GitHub...
git push origin main
if errorlevel 1 (
    echo ❌ Lỗi khi push!
    pause
    exit /b 1
)
echo ✅ Đã push thành công!

echo.
echo ╔════════════════════════════════════════╗
echo ║        ✨ Hoàn thành! ✨               ║
echo ║   Repository đã cập nhật trên GitHub   ║
echo ╚════════════════════════════════════════╝
echo.
pause
