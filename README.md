# Color Picker & Screen Marker — Bộ Công Cụ Tìm Màu

![Banner](assets/banner.png)

![Version](https://img.shields.io/badge/version-3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Bộ công cụ gồm **3 ứng dụng** độc lập, chia sẻ cùng engine phân loại màu AI 6 lõi, chạy nhẹ và tiện dụng trên Windows.

---

## 📦 Danh sách ứng dụng

| File | Tên | Mô tả |
|------|-----|--------|
| `ColorPicker.pyw` | **Color Picker** *(đầy đủ)* | Gộp cả Pick màu + Phân tích vùng + Clipboard |
| `ColorPicker_Pick.pyw` | **Color Picker — Pick** | Chỉ một chức năng: pick điểm màu với kính lúp |
| `Color Analyze.pyw` | **Color Analyze** | Vẽ vùng lasso + dán ảnh từ clipboard để phân tích màu |
| `ScreenMarker.pyw` | **Screen Marker** | Vẽ chú thích nhanh lên màn hình, chạy dưới System Tray |

---

## ✨ Tính năng chi tiết

### 🎯 Color Picker — Pick (`ColorPicker_Pick.pyw`)
- **Kính lúp Eyedropper:** Phóng to điểm ảnh, lưới pixel để pick màu chính xác.
- **Phân loại màu tức thì:** Trả về 1–3 nhóm màu khớp nhất (HSV + LAB DeltaE).
- **Copy HEX:** Click vào mã HEX để tự động copy vào clipboard.
- **Phím tắt:** `Alt + S` để mở kính lúp nhanh.

### 🖼️ Color Analyze (`Color Analyze.pyw`)
- **Vẽ vùng Lasso:** Vẽ tự do bao quanh vùng bất kỳ trên màn hình để phân tích màu.
- **Clipboard tự động:** Theo dõi clipboard, tự phân tích khi có ảnh mới copy vào.
- **Dán thủ công:** Nhấn `Ctrl + V` để phân tích ảnh đang có trong clipboard.
- **Kết quả đa màu:** Hiển thị màu chính + tối đa 2 màu phụ kèm % tin cậy.
- **Phím tắt:** `Alt + A` để mở vẽ vùng nhanh.

### 🎨 Color Picker *(đầy đủ)* (`ColorPicker.pyw`)
- Kết hợp toàn bộ tính năng của cả *Pick* và *Analyze*.
- `Alt + S`: kính lúp pick điểm | `Alt + A`: vẽ vùng lasso.

### 🤖 Engine AI Phân Loại Màu (dùng chung)
Hệ thống **Ensemble Voting 6 lõi**, phân loại vào **11 nhóm màu chuẩn** (Đỏ, Cam, Vàng, Xanh lá, Xanh dương, Tím, Hồng, Nâu, Xám, Trắng, Đen):
1. **Saliency Engine** — Ưu tiên màu có độ bão hòa cao
2. **Frequency Engine** — Màu xuất hiện nhiều nhất
3. **Core Engine** — Phân tích 50% vùng trung tâm ảnh
4. **BG Remove Engine** — Loại bỏ màu nền viền, tập trung chủ thể
5. **K-Means Engine** — Clustering tìm cụm màu chính
6. **LAB Expert Engine** — So sánh DeltaE trong không gian màu CIE L\*a\*b\*

### 🖍️ Screen Marker (`ScreenMarker.pyw`)
- **Chạy ngầm** dưới System Tray, không chiếm tài nguyên.
- **`Alt + D`** — Chụp màn hình hiện tại và mở canvas vẽ toàn màn hình.
- **Chuột trái kéo** — Vẽ tự do với bút chì tùy chỉnh.
- **Chuột phải kéo** — Di chuyển toàn bộ nét vẽ đến vị trí mới.
- **`Ctrl + Z`** — Undo nét vừa vẽ.
- **`Esc`** — Đóng canvas, quay lại chạy ngầm.

---

## 🛠️ Yêu cầu hệ thống

- **Hệ điều hành:** Windows 10/11 (DPI Awareness tích hợp sẵn)
- **Ngôn ngữ:** Python 3.13+
- **Thư viện:** `customtkinter`, `Pillow`, `numpy`, `keyboard`, `pystray`, `requests`

---

## 📥 Hướng dẫn cài đặt

1. Tải về hoặc clone repo.
2. Chạy `Install.bat` **một lần duy nhất** — tự động cài Python (nếu chưa có) và tất cả thư viện:
   ```powershell
   ./Install.bat
   ```
3. Double-click vào file `.pyw` muốn dùng để khởi động.

### Copy sang máy khác chỉ cần 4 file:
| File | Ghi chú |
|------|---------|
| `ColorPicker_Pick.pyw` | App pick màu |
| `Color Analyze.pyw` | App phân tích vùng |
| `Install.bat` | Cài đặt tự động |
| `requirements.txt` | Danh sách thư viện |

> *(Thêm `ScreenMarker.pyw` nếu cần dùng Screen Marker)*

---

## ⌨️ Bảng Phím Tắt Nhanh

| Phím tắt | Hành động | Ứng dụng |
|:---------|:----------|:---------|
| `Alt + S` | Mở kính lúp pick điểm màu | Color Picker / Pick |
| `Alt + A` | Mở vẽ vùng lasso | Color Picker / Analyze |
| `Ctrl + V` | Dán & phân tích ảnh clipboard | Color Picker / Analyze |
| `Esc` | Hủy / Đóng | Tất cả |
| `Alt + D` | Bật bút vẽ màn hình | Screen Marker |
| **Chuột trái kéo** | Vẽ tự do | Screen Marker |
| **Chuột phải kéo** | Di chuyển toàn bộ nét vẽ | Screen Marker |
| `Ctrl + Z` | Undo nét vẽ cuối | Screen Marker |

---

## 📦 Đóng gói thành .exe

Chạy `Build.bat` để đóng gói bằng PyInstaller:
```powershell
./Build.bat
```

---

## 📄 Giấy phép

MIT License — Tự do sử dụng, chỉnh sửa và phân phối.
