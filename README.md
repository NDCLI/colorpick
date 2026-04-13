# Color Picker - Bộ Công Cụ Nhận Diện Màu Sắc Đa Năng

![Banner](assets/banner.png)

![Version](https://img.shields.io/badge/version-2.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Color Picker** là một ứng dụng máy tính mạnh mẽ và tinh tế được thiết kế để giúp các nhà thiết kế, lập trình viên và nghệ sĩ dễ dàng nhận diện, phân tích và quản lý màu sắc. Ứng dụng tích hợp hệ thống **Ensemble AI Voting** cùng bảng màu hơn 120 gam màu (shades) chuyên nghiệp.

## ✨ Tính năng nổi bật

- **🔍 Kính lúp (Eyedropper):** Lấy mã màu chính xác từ bất kỳ điểm nào trên màn hình với độ thu phóng cao.
- **🤖 Ensemble AI Voting:** Sử dụng 6 thuật toán AI khác nhau để bầu chọn ra tên màu chính xác nhất cho hình ảnh.
- **📋 Tự động Clipboard:** Tự động phát hiện và phân tích khi bạn có hình ảnh mới trong bộ nhớ tạm (Clipboard).
- **🎨 120+ Gam màu chuyên nghiệp:** Phân loại chi tiết các sắc thái màu như Ruby, Navy, Emerald, Sunflower, v.v.
- **⚙️ Cài đặt linh hoạt:** Tùy chỉnh độ trong suốt, chế độ luôn hiện trên cùng (Always on top) và giao diện Sáng/Tối.
- **🚀 Phím tắt toàn cầu:** Kích hoạt nhanh tính năng lấy màu bằng tổ hợp phím **Alt + X** hoặc **Alt + S**.

## 🛠️ Yêu cầu hệ thống

- **Hệ điều hành:** Windows (Đã tối ưu hóa DPI Awareness).
- **Ngôn ngữ:** Python 3.13 trở lên.
- **Thư viện chính:** `customtkinter`, `Pillow`, `numpy`, `keyboard`.

## 📥 Hướng dẫn cài đặt

1. **Tải mã nguồn:** Tải bản ZIP hoặc clone repository này về máy.
2. **Cài đặt thư viện:** Chạy tệp `Install.bat` để hệ thống tự động thiết lập môi trường ảo và cài đặt các phụ thuộc cần thiết.
   ```powershell
   ./Install.bat
   ```

## 🚀 Cách sử dụng

- **Dán ảnh (Ctrl + V):** Sao chép bất kỳ tấm ảnh nào và dán vào ứng dụng để AI phân tích màu chu đạo.
- **Lấy màu nhanh (Alt + X / Alt + S):** Nhấn tổ hợp phím này để hiện kính lúp, di chuyển đến vị trí cần lấy màu và Click chuột trái để chọn.
- **Quản lý cài đặt:** Nhấn biểu tượng ⚙️ để tùy chỉnh giao diện và độ trong suốt của ứng dụng.

## ⌨️ Phím tắt nhanh

| Phím tắt | Chức năng |
| :--- | :--- |
| **Alt + X / Alt + S** | Kích hoạt công cụ lấy màu (Pick) |
| **Ctrl + V** | Dán ảnh từ Clipboard để phân tích |
| **Esc / Right Click** | Hủy chế độ Chọn điểm màu |

## 📦 Đóng gói ứng dụng (Build .exe)

Nếu bạn muốn đóng gói thành tệp thực thi duy nhất, hãy sử dụng PyInstaller với tệp `.spec` đi kèm:
```bash
pyinstaller ColorPicker.spec
```

## 📄 Giấy phép

Dự án này được phát hành dưới giấy phép MIT. Tự do sử dụng và phát triển thêm cho mục đích cá nhân hoặc thương mại.

---
