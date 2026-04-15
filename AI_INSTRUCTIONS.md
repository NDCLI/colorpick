# AI Project Instructions & Memory (Color Picker)

File này chứa các quy tắc quan trọng để bất kỳ AI nào (Antigravity hoặc các trợ lý khác) đều phải tuân thủ khi làm việc với dự án này, giúp đồng bộ hóa logic ngay cả khi bạn chuyển máy.

## 📌 Quy tắc Quản lý Phiên bản (Versioning)
- **File chính**: Luôn chỉ để một file source code mới nhất ở thư mục gốc (Ví dụ: `ColorPickerV2.4.pyw`).
- **Thư mục ARCHIVE**: Tất cả các phiên bản cũ hoặc file nháp phải được di chuyển vào thư mục `ARCHIVE` ngay khi có phiên bản mới hơn.
- **Build Script**: Luôn cập nhật file `Build.bat` để trỏ vào file `.pyw` mới nhất khi nâng cấp phiên bản.

## 🛠 Tính năng đặc biệt cần nhớ
1. **Lasso Tool (`Alt + A`)**: Cho phép vẽ vùng tự do. Phải đảm bảo các Engine AI (Saliency, K-Means, Lab) bỏ qua các pixel có Alpha = 0 (trong suốt).
2. **Precision Mouse Speed**: Khi bật Eyedropper (`Alt + S`) hoặc Lasso (`Alt + A`), phải giảm tốc độ chuột hệ thống xuống mức thấp (mức 3) để vẽ chính xác và **hoàn nguyên** ngay khi kết thúc/hủy.
3. **DPI Awareness**: Code luôn phải có đoạn xử lý `shcore` hoặc `user32` để chụp màn hình chính xác trên màn hình độ phân giải cao.

## 🚀 Quy trình làm việc của AI
1. **Đọc file này trước** khi thực hiện bất kỳ thay đổi nào.
2. **Không tự ý đổi Logic AI** trừ khi được yêu cầu rõ ràng.
3. **Giữ gìn sự sạch sẽ** của thư mục gốc.

---
*Cập nhật lần cuối: 2026-04-15 - Phiên bản hiện tại: v2.4*
