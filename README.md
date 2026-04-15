# Color Picker & Screen Marker - Bộ Công Cụ Tiện Ích Màn Hình

![Banner](assets/banner.png)

![Version](https://img.shields.io/badge/version-2.4-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Dự án bao gồm 2 công cụ chính: **Color Picker** (Nhận diện màu sắc đa năng với AI 6 lõi) và **Screen Marker** (Công cụ vẽ nhanh trên màn hình).

## ✨ Tính năng nổi bật

### 🎨 Color Picker v2.4
- **🤖 Tối ưu hoá với 11 Nhóm Màu Chuẩn:** Hệ thống Ensemble AI Voting phân loại chính xác 11 dải màu (Đỏ, Cam, Vàng, Xanh lá, Xanh dương, Tím, Hồng, Nâu, Xám, Trắng, Đen) thay vì 120 gam màu rườm rà.
- **🔍 Kính lúp (Eyedropper):** Phóng to điểm ảnh để lấy mã màu chính xác (Kích hoạt bằng `Alt + X` hoặc `Alt + S`).
- **👤 Tự động nhận diện (Context):** Nhận biết màu da người và màu áo (hiển thị cùng emoji 👤/👗), giúp phân tích đối tượng chính xác hơn.
- **📋 Tự động Clipboard:** Theo dõi bộ nhớ tạm và tự động phân tích khi có ảnh copy mới.

### 🖍️ Screen Marker
- **Chạy ngầm nhẹ nhàng:** Hoạt động dưới System Tray, sẵn sàng mọi lúc.
- **Vẽ nhanh (Draw overlay):** Cố định màn hình hiện tại và vẽ chú thích lên đó ngay lập tức với phím tắt `Alt + D`.
- **Hoàn tác (Undo):** Dễ dàng xóa các nét vừa vẽ với `Ctrl + Z` hoặc nhấn `Esc` để đóng.

## 🛠️ Yêu cầu hệ thống

- **Hệ điều hành:** Windows (đã tối ưu hóa DPI Awareness).
- **Ngôn ngữ:** Python 3.13+.
- **Thư viện chính:** `customtkinter`, `Pillow`, `numpy`, `keyboard`, `pystray`.

## 📥 Hướng dẫn cài đặt

1. Giải nén thư mục tải về.
2. Chạy tệp `Install.bat` (chỉ cần chạy một lần duy nhất). Hệ thống sẽ tự động thiết lập Python Virtual Environment và cài đặt các phụ thuộc cần thiết.
   ```powershell
   ./Install.bat
   ```

## 🚀 Cách sử dụng

### Color Picker
- **Khởi động:** Chạy `ColorPickerV2.4.pyw` (hoặc thông qua shortcut nếu đã build).
- **Phân tích:** Nhấn `Ctrl + V` để dán ảnh. AI sẽ tự động phân tích qua 6 lõi (Saliency, Frequency, Core, BG Remove, K-Means, LAB Expert).
- **Cài đặt:** Nhấn biểu tượng ⚙️ góc phải để tùy chỉnh giao diện (Sáng/Tối/Trong suốt).

### Screen Marker
- **Khởi động:** Chạy tệp `ScreenMarker.pyw` (sẽ xuất hiện biểu tượng nhỏ ở góc khay hệ thống - System Tray).
- **Vẽ lên màn hình:** Bấm `Alt + D` để biến chuột thành bút vẽ.
- **Thoát vẽ:** Nhấn `Esc`. Đóng hoàn toàn bằng cách click chuột phải vào icon ở Tray -> Thoát.

## ⌨️ Bảng Phím Tắt Nhanh

| Chức năng | Phím tắt / Thao tác | Ứng dụng |
| :--- | :--- | :--- |
| **Bật kính lúp lấy màu** | `Alt + X` hoặc `Alt + S` | Color Picker |
| **Phân tích ảnh Clipboard** | `Ctrl + V` | Color Picker |
| **Hủy chọn kính lúp** | `Esc` hoặc `Click chuột phải` | Color Picker |
| **Bật bút vẽ màn hình** | `Alt + D` | Screen Marker |
| **Hoàn tác nét vẽ (Undo)** | `Ctrl + Z` | Screen Marker |
| **Thoát bút vẽ màn hình** | `Esc` | Screen Marker |

## 📦 Đóng gói ứng dụng (Build .exe)

Bạn có thể tạo tệp `.exe` độc lập bằng `pyinstaller` hoặc chạy tệp `Build.bat` để đóng gói tự động thành phần bạn muốn (kiểm tra tệp `.spec` đi kèm).

## 📄 Giấy phép

Dự án này được phát hành dưới giấy phép MIT. Tự do sử dụng và phát triển thêm cho mục đích cá nhân hoặc thương mại.

---
