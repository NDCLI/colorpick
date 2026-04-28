"""
Auto-Update Module cho Color Picker
Kiểm tra phiên bản mới từ GitHub và cập nhật tự động
"""

import os
import sys
import json
import requests
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import time
import signal

# ===== CẤU HÌNH =====
GITHUB_REPO = "NDCLI/colorpick"
UPDATE_CHECK_FILE = os.path.join(os.path.dirname(__file__), ".update_check.json")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")
LOG_FILE = os.path.join(os.path.dirname(__file__), ".update_log.txt")
VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.txt")

# Version hiện tại (đọc từ file version.txt)
def get_current_version():
    """Đọc version từ file version.txt"""
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except:
        return "2.4"  # Default fallback

def log_message(message):
    """Ghi log vào file (debug purpose)"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

def find_app_file():
    """Tìm file .pyw app (ưu tiên file đang thực thi)"""
    try:
        # sys.argv[0] chứa đường dẫn file đang chạy
        main_file = os.path.abspath(sys.argv[0])
        if main_file.endswith(".pyw") and os.path.exists(main_file):
            return main_file
    except Exception:
        pass

    # Fallback: Tìm file .pyw đầu tiên trong thư mục
    app_dir = os.path.dirname(__file__)
    for file in os.listdir(app_dir):
        if file.endswith(".pyw") and "updater" not in file:
            return os.path.join(app_dir, file)
    return None

def get_latest_release():
    """Lấy thông tin release mới nhất từ GitHub API"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_message(f"Error fetching release: {e}")
        return None

def parse_version(version_str):
    """Chuyển đổi string phiên bản sang tuple để so sánh"""
    try:
        version_str = version_str.lstrip('vV')
        return tuple(map(int, version_str.split('.')))
    except:
        return (0,)

def show_update_dialog(version_name):
    """Hiển thị dialog hỏi người dùng có muốn cập nhật"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        
        result = messagebox.askokcancel(
            "Cập nhật phiên bản",
            f"Có phiên bản mới {version_name} của Color Picker!\n\n"
            "Bạn có muốn cập nhật ngay không?\n"
            "(Ứng dụng sẽ khởi động lại sau khi cập nhật)"
        )
        root.destroy()
        return result
    except:
        return False

def download_file(url, filepath):
    """Tải file từ URL"""
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        log_message(f"Download error: {e}")
        return False

def backup_current_version():
    """Sao lưu phiên bản hiện tại"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        current_file = find_app_file()
        if not current_file or not os.path.exists(current_file):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_filename = os.path.splitext(os.path.basename(current_file))[0]
        backup_file = os.path.join(BACKUP_DIR, f"{app_filename}_backup_{timestamp}.pyw")
        
        shutil.copy2(current_file, backup_file)
        return backup_file
    except Exception as e:
        log_message(f"Backup error: {e}")
        return None

def update_app(download_url, status_callback=None):
    """Cập nhật ứng dụng"""
    def set_status(msg):
        if status_callback: status_callback(msg)
        log_message(msg)

    try:
        set_status("⏳ Đang tải bản cập nhật...")
        current_file = find_app_file()
        if not current_file:
            return False
        
        backup_file = backup_current_version()
        if not backup_file:
            set_status("❌ Lỗi: Không thể sao lưu file cũ")
            return False

        app_filename = os.path.basename(current_file)
        temp_file = os.path.join(os.path.dirname(__file__), f"{app_filename}_update")
        
        if not download_file(download_url, temp_file):
            set_status("❌ Lỗi: Tải xuống thất bại")
            return False
        
        try:
            shutil.copy2(temp_file, current_file)
            os.remove(temp_file)
        except Exception:
            try:
                shutil.move(temp_file, current_file)
            except Exception as e:
                set_status(f"❌ Lỗi ghi đè file: {e}")
                return False
        
        return True
    except Exception as e:
        set_status(f"❌ Lỗi hệ thống: {e}")
        return False

def record_check_time():
    """Ghi lại thời gian kiểm tra cuối cùng"""
    try:
        with open(UPDATE_CHECK_FILE, 'w') as f:
            json.dump({"last_check": datetime.now().isoformat()}, f)
    except:
        pass

def check_for_updates(status_callback=None):
    """Hàm chính: Kiểm tra và cập nhật nếu cần"""
    def set_status(msg):
        if status_callback: status_callback(msg)
        log_message(msg)

    try:
        set_status("🔍 Đang kiểm tra cập nhật...")
        record_check_time()
        
        release = get_latest_release()
        if not release:
            set_status("⚠️ Không thể kết nối máy chủ cập nhật")
            return
        
        tag_name = release.get("tag_name", "0.0")
        latest_version = parse_version(tag_name)
        current_version_str = get_current_version()
        current_version = parse_version(current_version_str)
        
        if latest_version > current_version:
            set_status(f"✨ Có bản cập nhật mới: {tag_name}")
            
            if show_update_dialog(tag_name):
                download_url = None
                for asset in release.get("assets", []):
                    if asset["name"].endswith(".pyw"):
                        download_url = asset["browser_download_url"]
                        break
                
                if download_url:
                    if update_app(download_url, status_callback):
                        try:
                            # Cập nhật version.txt
                            new_version = tag_name.lstrip('vV')
                            with open(VERSION_FILE, 'w') as f:
                                f.write(new_version)
                        except: pass
                        
                        set_status("✅ Cập nhật thành công! Đang khởi động lại...")
                        app_file = find_app_file()
                        time.sleep(1.5)
                        subprocess.Popen([sys.executable, app_file])
                        os._exit(0)
                    else:
                        set_status("❌ Cập nhật thất bại")
                else:
                    set_status("❌ Lỗi: Không thấy file cài đặt trên GitHub")
            else:
                set_status("Đã hủy cập nhật")
        else:
            set_status("🚀 Ứng dụng đã ở bản mới nhất")
    
    except Exception as e:
        set_status(f"❌ Lỗi: {str(e)}")


if __name__ == "__main__":
    # Test
    check_for_updates()
