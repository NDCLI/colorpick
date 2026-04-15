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
    """Tìm file .pyw app (loại trừ updater.py)"""
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
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        log_message(f"GitHub API response OK: {response.status_code}")
        return response.json()
    except requests.exceptions.ConnectionError as e:
        log_message(f"Connection error: {e}")
        return None
    except requests.exceptions.Timeout:
        log_message("GitHub API timeout")
        return None
    except Exception as e:
        log_message(f"Error fetching release: {e}")
        return None

def parse_version(version_str):
    """Chuyển đổi string phiên bản sang tuple để so sánh"""
    try:
        # Loại bỏ 'v' hoặc 'V' nếu có (v2.4 hoặc V2.4 -> 2.4)
        version_str = version_str.lstrip('vV')
        return tuple(map(int, version_str.split('.')))
    except:
        return (0,)

def show_update_dialog():
    """Hiển thị dialog hỏi người dùng có muốn cập nhật"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askokcancel(
            "Cập nhật phiên bản",
            "Có phiên bản mới của Color Picker!\n\n"
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
        log_message(f"Downloading from: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        log_message(f"Downloaded {downloaded} bytes to {filepath}")
        return True
    except Exception as e:
        log_message(f"Download error: {e}")
        return False

def backup_current_version():
    """Sao lưu phiên bản hiện tại"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Tìm file app hiện tại
        current_file = find_app_file()
        if not current_file or not os.path.exists(current_file):
            log_message("ERROR: Current app file not found for backup")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_filename = os.path.splitext(os.path.basename(current_file))[0]
        backup_file = os.path.join(BACKUP_DIR, f"{app_filename}_backup_{timestamp}.pyw")
        
        shutil.copy2(current_file, backup_file)
        log_message(f"Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        log_message(f"Backup error: {e}")
        return None

def update_app(download_url):
    """Cập nhật ứng dụng"""
    try:
        log_message("⏳ Downloading update...")
        
        # Tìm file app hiện tại
        current_file = find_app_file()
        if not current_file:
            log_message("ERROR: Could not find app file to update")
            return False
        
        log_message(f"Found app file: {current_file}")
        
        # Sao lưu file cũ
        backup_file = backup_current_version()
        
        # Tải file mới
        app_filename = os.path.basename(current_file)
        temp_file = os.path.join(os.path.dirname(__file__), f"{app_filename}_update")
        if not download_file(download_url, temp_file):
            log_message("Download failed")
            return False
        
        log_message(f"Downloaded to: {temp_file}")
        
        # Thay thế file cũ (copy + delete để tránh permission issues)
        try:
            shutil.copy2(temp_file, current_file)
            os.remove(temp_file)
            log_message(f"Update complete: {current_file}")
        except Exception as e:
            log_message(f"Copy/Replace error: {e}")
            # Fallback: dùng move
            try:
                shutil.move(temp_file, current_file)
                log_message("Update complete (via move)")
            except Exception as e2:
                log_message(f"Move error: {e2}")
                return False
        
        log_message("✅ Update successful!")
        return True
    except Exception as e:
        log_message(f"ERROR in update_app: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

def record_check_time():
    """Ghi lại thời gian kiểm tra cuối cùng"""
    try:
        with open(UPDATE_CHECK_FILE, 'w') as f:
            json.dump({"last_check": datetime.now().isoformat()}, f)
    except:
        pass

def should_check_update():
    """Kiểm tra xem có nên kiểm tra cập nhật ngay không"""
    # Kiểm tra mỗi lần khởi động (có thể thêm logic kiểm tra thời gian nếu muốn)
    return True

def check_for_updates():
    """Hàm chính: Kiểm tra và cập nhật nếu cần"""
    try:
        # Kiểm tra xem có nên kiểm tra không
        if not should_check_update():
            log_message("Skip update check")
            return
        
        log_message("=== Starting update check ===")
        record_check_time()
        
        # Lấy thông tin release mới nhất
        release = get_latest_release()
        if not release:
            log_message("No release info found from GitHub")
            return
        
        latest_version = parse_version(release.get("tag_name", "0.0"))
        current_version = parse_version(get_current_version())
        
        log_message(f"Latest version: {release['tag_name']}, Current version: {get_current_version()}")
        
        # So sánh phiên bản
        if latest_version > current_version:
            log_message(f"New version available: {release['tag_name']}")
            
            # Hỏi người dùng
            if show_update_dialog():
                log_message("User accepted update")
                # Tìm file .pyw trong release assets
                download_url = None
                for asset in release.get("assets", []):
                    if asset["name"].endswith(".pyw"):
                        download_url = asset["browser_download_url"]
                        log_message(f"Found asset: {asset['name']}")
                        break
                
                if download_url:
                    if update_app(download_url):
                        # Cập nhật version.txt để không hỏi cập nhật lại lần tới
                        try:
                            new_version = release.get("tag_name", "0.0").lstrip('vV')
                            with open(VERSION_FILE, 'w') as f:
                                f.write(new_version)
                            log_message(f"Updated version file to: {new_version}")
                        except Exception as e:
                            log_message(f"Warning: Could not update version file: {e}")
                        
                        # Khởi động lại ứng dụng
                        log_message("Update successful, restarting app...")
                        
                        # Tìm file app hiện tại
                        app_file = find_app_file()
                        if not app_file:
                            log_message("ERROR: Could not find app file")
                            return
                        
                        log_message(f"Restarting app: {app_file}")
                        
                        # Chờ trước khi restart
                        time.sleep(1)
                        
                        # Start app mới trong process mới
                        subprocess.Popen([sys.executable, app_file])
                        
                        # Force exit process hiện tại (để app cũ không chiếm mutex)
                        log_message("Forcing main process exit...")
                        os._exit(0)
                else:
                    log_message("ERROR: No .pyw file found in release assets")
            else:
                log_message("User declined update")
        else:
            log_message("Already on latest version")
    
    except Exception as e:
        log_message(f"ERROR: {str(e)}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Test
    check_for_updates()
