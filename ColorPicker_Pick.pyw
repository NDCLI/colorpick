import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import ImageGrab, Image, ImageStat, ImageDraw, ImageTk
import collections
import colorsys
import json
import os
import sys
import ctypes
import numpy as np
import threading
import ctypes.wintypes
import atexit

# --- DIEU CHINH TOC DO CHUOT ---
SPI_GETMOUSESPEED = 112
SPI_SETMOUSESPEED = 113
original_mouse_speed = None
precision_mouse_speed = 4.2

def get_mouse_speed():
    try:
        speed = ctypes.c_int()
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0)
        return speed.value
    except:
        return 10

def set_mouse_speed(speed):
    try:
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)
    except: ...

def enable_precision_mouse():
    global original_mouse_speed
    if original_mouse_speed is None:
        original_mouse_speed = get_mouse_speed()
        set_mouse_speed(precision_mouse_speed)

def restore_mouse_speed():
    global original_mouse_speed
    if original_mouse_speed is not None:
        set_mouse_speed(original_mouse_speed)
        original_mouse_speed = None

atexit.register(restore_mouse_speed)

# DPI Awareness cho Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ==========================================
# v2.5 - LOGIC MAU MOI (11 NHOM MAU CHUAN)
# ==========================================

def single_instance_check():
    mutex_name = r"Global\ColorPicker_Pick_Unique_Mutex"
    ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183:
        temp_root = ctk.CTk()
        temp_root.withdraw()
        messagebox.showinfo("Color Picker - Pick", "Ứng dụng đang chạy rồi bạn nhé!")
        sys.exit(0)

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(get_app_dir(), "settings_pick.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"topmost": False, "opacity": 1.0, "theme": "System"}

def save_settings(topmost, opacity, theme="System"):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"topmost": topmost, "opacity": float(opacity),
                       "theme": theme}, f)
    except:
        pass

# ==========================================
# DINH NGHIA 11 NHOM MAU
# ==========================================

COLOR_FAMILIES = {
    "Red":    "#C0392B",
    "Orange": "#E67E22",
    "Yellow": "#F1C40F",
    "Green":  "#27AE60",
    "Blue":   "#2980B9",
    "Purple": "#8E44AD",
    "Pink":   "#FF69B4",
    "Brown":  "#795548",
    "Gray":   "#95A5A6",
    "White":  "#F5F5F5",
    "Black":  "#1C1C1C",
}

# LAB gia tri tham chieu cho tung nhom mau (Expert Engine)
LAB_REFERENCE = {
    "Red":    (40.0,  61.5,  45.0),
    "Orange": (62.0,  35.0,  68.0),
    "Yellow": (83.0,   3.0,  82.0),
    "Green":  (51.0, -50.0,  44.0),
    "Blue":   (42.0,   6.0, -52.0),
    "Purple": (32.0,  48.0, -52.0),
    "Pink":   (65.5,  64.0, -11.0),
    "Brown":  (35.0,  18.0,  24.0),
    "Gray":   (62.0,   0.0,   0.0),
    "White":  (96.0,   0.0,   0.0),
    "Black":  ( 8.0,   0.0,   0.0),
}

# ==========================================
# ENGINE MAU - LOGIC PHAN LOAI CHINH
# ==========================================

def classify_pixel(rgb):
    """
    Phan loai 1 pixel vao 1 trong 11 nhom mau (AI Logic v2).
    Tra ve: (ten_nhom_mau, do_bao_hoa)
    """
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h_deg = h * 360

    # --- ACHROMATIC ---
    if v < 0.15:
        return "Black", s
    if v < 0.20 and s < 0.20:
        return "Black", s
    if v > 0.90 and s < 0.06:
        return "White", s
    if v > 0.85 and s < 0.08:
        return "White", s
    if s < 0.05:
        if v >= 0.80:
            return "White", s
        if v <= 0.20:
            return "Black", s
        return "Gray", s
    if s < 0.10:
        if v >= 0.88:
            return "White", s
        if v <= 0.22:
            return "Black", s
        return "Gray", s

    # --- CHROMATIC ---
    # == RED zone: 338-360 and 0-12 ==
    if h_deg >= 338 or h_deg < 12:
        if s < 0.36 and v > 0.75:
            return "Pink", s
        if v < 0.35:
            return ("Brown", s) if h_deg < 10 else ("Red", s)
        if v < 0.55 and s > 0.50:
            return "Brown", s
        return "Red", s

    # == PINK: 295-338 ==
    if h_deg >= 295:
        if v < 0.45:
            return "Purple", s
        if h_deg < 315 and v < 0.65 and s > 0.50:
            return "Purple", s
        return "Pink", s

    # == ORANGE + BROWN: 12-45 ==
    if h_deg < 45:
        if v < 0.45:
            return "Brown", s
        if v < 0.65:
            if s > 0.60:
                return ("Orange", s) if v > 0.55 else ("Brown", s)
            return "Brown", s
        if s < 0.25 and v < 0.82:
            return "Brown", s
        return "Orange", s

    # == YELLOW: 45-70 ==
    if h_deg < 70:
        if v < 0.40 and h_deg < 60:
            return "Brown", s
        if v < 0.58 and s < 0.45 and h_deg < 60:
            return "Brown", s
        if h_deg > 60 and s > 0.50 and v < 0.50:
            return "Green", s
        return "Yellow", s

    # == YELLOW-GREEN: 70-85 ==
    if h_deg < 85:
        if s > 0.30:
            return "Green", s
        return "Yellow", s

    # == GREEN: 85-170 ==
    if h_deg < 170:
        return "Green", s

    # == BLUE: 170-245 ==
    if h_deg < 245:
        return "Blue", s

    # == PURPLE: 245-295 ==
    if h_deg < 315:
        if h_deg > 300 and s < 0.20 and v > 0.80:
            return "Pink", s
        return "Purple", s

    return "Gray", s


# ==========================================
# CHUYEN DOI MAU - RGB -> LAB -> DeltaE
# ==========================================

def rgb_to_lab(rgb):
    def pivot_rgb(c):
        c = c / 255.0
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    def pivot_xyz(v):
        return v ** (1 / 3) if v > 0.008856 else (7.787 * v) + (16 / 116)

    r, g, b = (pivot_rgb(c) for c in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    fx, fy, fz = pivot_xyz(x), pivot_xyz(y), pivot_xyz(z)
    L = max(0.0, (116 * fy) - 16)
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return (L, a, b_val)


def delta_e(lab_a, lab_b):
    return sum((x - y) ** 2 for x, y in zip(lab_a, lab_b)) ** 0.5


def get_family_hex(name):
    """Tra ve hex dai dien cho nhom mau (an toan, khong crash)."""
    return COLOR_FAMILIES.get(name, "#808080")


def get_top_matches(rgb, threshold=18.0):
    """
    Tra ve 1-3 ten nhom mau cho 1 diem anh (cho eyedropper).
    Ket hop HSV + LAB de co ket qua chinh xac nhat.
    """
    hsv_name, _ = classify_pixel(rgb)

    lab_val = rgb_to_lab(rgb)
    dists = sorted((delta_e(lab_val, ref), name) for name, ref in LAB_REFERENCE.items())

    results = [hsv_name]
    for dist, name in dists:
        if name not in results and (dist - dists[0][0]) < threshold:
            results.append(name)
        if len(results) >= 3:
            break

    return results


# ==========================================
# GIAO DIEN (UI) - BAN PICK MAU
# ==========================================

def copy_point_hex():
    if picked_point_color:
        app.clipboard_clear()
        app.clipboard_append(picked_point_color)
        app.update()
        status_dot.configure(fg_color="dodgerblue")


def toggle_pin():
    app.attributes("-topmost", pin_var.get())
    save_settings(pin_var.get(), current_opacity, current_theme)


def change_opacity(value):
    global current_opacity
    current_opacity = float(value)
    app.attributes("-alpha", current_opacity)
    save_settings(pin_var.get(), current_opacity, current_theme)
    if settings_opacity_val_label:
        settings_opacity_val_label.configure(text=f"{int(current_opacity * 100)}%")


settings_window_ref = None
settings_opacity_val_label = None


def open_settings():
    global settings_window_ref, settings_opacity_val_label
    if settings_window_ref is not None and settings_window_ref.winfo_exists():
        settings_window_ref.lift()
        settings_window_ref.focus_force()
        return

    sw = ctk.CTkToplevel(app)
    sw.title("Cài đặt")
    sw.geometry("320x300")
    sw.resizable(False, False)
    sw.attributes("-topmost", True)
    sw.grab_set()
    sw.focus_force()
    settings_window_ref = sw

    def on_close():
        global settings_window_ref
        settings_window_ref = None
        sw.destroy()

    sw.protocol("WM_DELETE_WINDOW", on_close)
    ctk.CTkLabel(sw, text="⚙️ Cài đặt", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 10))

    ctk.CTkLabel(sw, text="Độ trong suốt:", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20)
    opacity_row = ctk.CTkFrame(sw, fg_color="transparent")
    opacity_row.pack(fill="x", padx=20, pady=(4, 8))

    settings_opacity_val_label = ctk.CTkLabel(
        opacity_row, text=f"{int(current_opacity * 100)}%",
        font=ctk.CTkFont(size=12), width=40
    )
    settings_opacity_val_label.pack(side="right")
    sld = ctk.CTkSlider(opacity_row, from_=0.3, to=1.0, command=change_opacity)
    sld.set(current_opacity)
    sld.pack(side="left", expand=True, fill="x", padx=(0, 8))

    sep = ctk.CTkFrame(sw, height=1, fg_color="gray40")
    sep.pack(fill="x", padx=20, pady=(4, 10))

    def set_theme(choice):
        global current_theme
        current_theme = choice
        ctk.set_appearance_mode(choice)
        save_settings(pin_var.get(), current_opacity, current_theme)

    ctk.CTkLabel(sw, text="Giao diện (Theme):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
    theme_row = ctk.CTkFrame(sw, fg_color="transparent")
    theme_row.pack(fill="x", padx=15)
    theme_seg = ctk.CTkSegmentedButton(
        theme_row,
        values=["Sáng", "Tối", "Hệ thống"],
        command=lambda v: set_theme({"Sáng": "Light", "Tối": "Dark", "Hệ thống": "System"}[v])
    )
    theme_seg.set({"Light": "Sáng", "Dark": "Tối", "System": "Hệ thống"}[current_theme])
    theme_seg.pack(expand=True, fill="x", pady=5)

    ctk.CTkButton(
        sw, text="Hoàn tất", width=120, height=32,
        fg_color="#6366f1", hover_color="#4f46e5",
        command=on_close
    ).pack(pady=(25, 0))


def reset_app():
    point_color_hex_label.configure(text="")
    point_color_name_label.configure(text="")
    point_color_box.configure(fg_color="gray20")
    point_copy_btn.pack_forget()
    point_color_frame.pack_forget()
    status_dot.configure(fg_color="green")


# ==========================================
# EYEDROPPER (CHON DIEM MAU)
# ==========================================

eyedropper_active    = False
eyedropper_overlay   = None
eyedropper_loupe     = None
eyedropper_canvas    = None
eyedropper_hex_label = None
eyedropper_screenshot = None

MAG_RADIUS     = 45
MAG_GRID_COUNT = 13


def start_eyedropper():
    global eyedropper_active
    if eyedropper_active:
        return
    eyedropper_active = True
    app.withdraw()
    app.after(180, _launch_eyedropper)


def _launch_eyedropper():
    global eyedropper_overlay, eyedropper_loupe, eyedropper_canvas
    global eyedropper_hex_label, eyedropper_screenshot

    try:
        eyedropper_screenshot = ImageGrab.grab()
    except Exception:
        cleanup_eyedropper()
        return

    enable_precision_mouse()
    
    scr_w = eyedropper_screenshot.width
    scr_h = eyedropper_screenshot.height
    loupe_size = MAG_RADIUS * 2 + 4

    overlay = tk.Toplevel()
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.01)
    overlay.geometry(f"{scr_w}x{scr_h}+0+0")
    overlay.configure(cursor="crosshair", bg="black")
    eyedropper_overlay = overlay

    loupe = tk.Toplevel()
    loupe.overrideredirect(True)
    loupe.attributes("-topmost", True)
    loupe.attributes("-transparentcolor", "magenta")
    loupe.configure(bg="magenta")
    loupe.geometry(f"{loupe_size}x{loupe_size + 28}+0+0")
    eyedropper_loupe = loupe

    canvas = tk.Canvas(loupe, width=loupe_size, height=loupe_size,
                       bg="magenta", highlightthickness=0, cursor="none")
    canvas.pack()
    eyedropper_canvas = canvas

    hex_lbl = tk.Label(loupe, text="#000000",
                       font=("Consolas", 10, "bold"),
                       fg="white", bg="#1a1a1a", padx=6, pady=2)
    hex_lbl.pack()
    eyedropper_hex_label = hex_lbl

    overlay.bind("<Motion>",   _on_motion)
    overlay.bind("<Button-1>", _on_click)
    overlay.bind("<Button-3>", _on_cancel)
    overlay.bind("<Escape>",   _on_cancel)
    overlay.focus_force()

    mx = overlay.winfo_pointerx()
    my = overlay.winfo_pointery()
    _move_loupe(mx, my)
    _draw_loupe(mx, my)


def _on_motion(event):
    _move_loupe(event.x_root, event.y_root)
    _draw_loupe(event.x_root, event.y_root)


def _move_loupe(mx, my):
    if eyedropper_loupe is None:
        return
    loupe_size = MAG_RADIUS * 2 + 4
    eyedropper_loupe.geometry(f"+{mx - loupe_size // 2}+{my - loupe_size // 2}")


def _draw_loupe(mx, my):
    if eyedropper_screenshot is None or eyedropper_canvas is None:
        return
    scr_w = eyedropper_screenshot.width
    scr_h = eyedropper_screenshot.height
    half = MAG_GRID_COUNT // 2
    loupe_size = MAG_RADIUS * 2 + 4

    left   = max(0, mx - half)
    top    = max(0, my - half)
    right  = min(scr_w, mx + half + 1)
    bottom = min(scr_h, my + half + 1)

    crop   = eyedropper_screenshot.crop((left, top, right, bottom))
    zoomed = crop.resize((loupe_size, loupe_size), Image.NEAREST)

    mask = Image.new("L", (loupe_size, loupe_size), 0)
    ImageDraw.Draw(mask).ellipse([2, 2, loupe_size - 3, loupe_size - 3], fill=255)
    final = Image.new("RGB", (loupe_size, loupe_size), (255, 0, 255))
    final.paste(zoomed, (0, 0), mask)

    draw = ImageDraw.Draw(final)
    cell = loupe_size / MAG_GRID_COUNT
    for i in range(MAG_GRID_COUNT + 1):
        p = int(i * cell)
        draw.line([(p, 0), (p, loupe_size)], fill=(60, 60, 60), width=1)
        draw.line([(0, p), (loupe_size, p)], fill=(60, 60, 60), width=1)

    cx0 = int(half * cell);     cy0 = int(half * cell)
    cx1 = int((half + 1) * cell); cy1 = int((half + 1) * cell)
    draw.rectangle([cx0 - 1, cy0 - 1, cx1 + 1, cy1 + 1], outline="#000000", width=1)
    draw.rectangle([cx0,     cy0,     cx1,     cy1    ], outline="#FFFFFF", width=1)

    final2 = Image.new("RGB", (loupe_size, loupe_size), (255, 0, 255))
    final2.paste(final, (0, 0), mask)
    ImageDraw.Draw(final2).ellipse([1, 1, loupe_size - 2, loupe_size - 2], outline="#333333", width=2)
    ImageDraw.Draw(final2).ellipse([0, 0, loupe_size - 1, loupe_size - 1], outline="#888888", width=1)

    tk_img = ImageTk.PhotoImage(final2)
    eyedropper_canvas.delete("all")
    eyedropper_canvas.create_image(loupe_size // 2, loupe_size // 2, image=tk_img)
    eyedropper_canvas._ref = tk_img

    try:
        r, g, b = eyedropper_screenshot.getpixel((mx, my))[:3]
        eyedropper_hex_label.configure(text=f"#{r:02X}{g:02X}{b:02X}")
    except Exception:
        pass


def _on_click(event):
    mx, my = event.x_root, event.y_root
    try:
        px = eyedropper_screenshot.getpixel((mx, my))
        r, g, b = px[0], px[1], px[2]
    except Exception:
        cleanup_eyedropper()
        return
    hex_color = f"#{r:02X}{g:02X}{b:02X}"
    names = get_top_matches((r, g, b), threshold=18.0)
    cleanup_eyedropper()
    render_point_color((r, g, b), hex_color, names)


def _on_cancel(event=None):
    cleanup_eyedropper()


def cleanup_eyedropper():
    global eyedropper_active, eyedropper_overlay, eyedropper_loupe
    global eyedropper_canvas, eyedropper_hex_label, eyedropper_screenshot
    restore_mouse_speed()
    eyedropper_active = False
    for win in [eyedropper_loupe, eyedropper_overlay]:
        if win is not None:
            try:
                win.destroy()
            except Exception:
                pass
    eyedropper_overlay = eyedropper_loupe = None
    eyedropper_canvas  = eyedropper_hex_label = None
    eyedropper_screenshot = None
    app.deiconify()
    app.lift()
    app.focus_force()


def render_point_color(rgb, hex_color, color_names):
    global picked_point_color
    picked_point_color = hex_color
    point_color_box.configure(fg_color=hex_color)
    point_color_hex_label.configure(text=hex_color)

    parts = []
    seen = set()
    for name in color_names:
        clean = name.upper()
        if clean not in seen:
            parts.append(clean)
            seen.add(clean)
    point_color_name_label.configure(text=" / ".join(parts))

    point_color_frame.pack(pady=(2, 0), fill="x", padx=15)
    status_dot.configure(fg_color="#6366f1")


# ==========================================
# KHOI TAO UI
# ==========================================

picked_point_color = None
app_settings = load_settings()
current_opacity = app_settings.get("opacity", 1.0)
current_theme   = app_settings.get("theme", "System")

ctk.set_appearance_mode(current_theme)
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Color Picker - Pick v3.0")
app.geometry("360x200")
app.attributes("-alpha", current_opacity)
app.attributes("-topmost", app_settings.get("topmost", False))
app.minsize(340, 180)

# Top toolbar
top_frame = ctk.CTkFrame(app, fg_color="transparent")
top_frame.pack(fill="x", padx=15, pady=(10, 5))

pin_var = ctk.BooleanVar(value=app_settings.get("topmost", False))
ctk.CTkSwitch(top_frame, text="Ghim", variable=pin_var, command=toggle_pin).pack(side="left")

ctk.CTkButton(
    top_frame, text="🎯 Pick", width=50, height=25,
    fg_color="#6366f1", hover_color="#4f46e5",
    font=ctk.CTkFont(size=12, weight="bold"),
    command=start_eyedropper
).pack(side="left", padx=8)

ctk.CTkButton(
    top_frame, text="⚙️", width=28, height=26,
    fg_color="#334155", hover_color="#475569",
    font=ctk.CTkFont(size=12),
    command=open_settings
).pack(side="right", padx=(4, 0))

ctk.CTkButton(
    top_frame, text="Reset", width=46, height=24,
    fg_color="#c0392b", hover_color="#e74c3c",
    font=ctk.CTkFont(size=11),
    command=reset_app
).pack(side="right", padx=(0, 4))

# Point color picked
point_color_frame = ctk.CTkFrame(app, fg_color="transparent")

ctk.CTkLabel(
    point_color_frame, text="🎯 Color Picked:",
    font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70"
).pack(anchor="w", padx=5)

point_color_inner = ctk.CTkFrame(point_color_frame, fg_color="transparent")
point_color_inner.pack(fill="x", padx=5, pady=5)

point_color_box = ctk.CTkFrame(point_color_inner, width=60, height=60, corner_radius=6, fg_color="gray20")
point_color_box.pack(side="left", padx=(0, 12))

point_color_hex_label = ctk.CTkLabel(
    point_color_inner, text="",
    font=ctk.CTkFont(family="Consolas", size=14, weight="bold")
)
point_color_hex_label.pack(side="left", padx=(0, 6))
point_color_hex_label.bind("<Button-1>", lambda e: copy_point_hex())

point_color_name_label = ctk.CTkLabel(
    point_color_inner, text="",
    font=ctk.CTkFont(size=12), text_color="gray70"
)
point_color_name_label.pack(side="left")

point_copy_btn = ctk.CTkButton(
    point_color_frame, text="Copy HEX", width=80, height=22,
    fg_color="#6366f1", hover_color="#4f46e5", font=ctk.CTkFont(size=10),
    command=copy_point_hex
)

status_dot = ctk.CTkFrame(app, width=10, height=10, corner_radius=5, fg_color="green")

# Hotkey label
hotkey_label = ctk.CTkLabel(
    app, text="⌨️ Nhấn Alt+S ",
    font=ctk.CTkFont(size=11), text_color="gray60"
)
hotkey_label.pack(pady=(5, 0))

# ==========================================
# WIN32 HOTKEY LISTENER (Alt+S)
# ==========================================

def start_hotkey_listener():
    def listener():
        user32 = ctypes.windll.user32
        MOD_ALT = 0x0001
        VK_S = 0x53
        user32.RegisterHotKey(None, 1, MOD_ALT, VK_S)
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:
                    if msg.wParam == 1:
                        app.after(0, start_eyedropper)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)

    threading.Thread(target=listener, daemon=True).start()


if __name__ == "__main__":
    single_instance_check()
    start_hotkey_listener()
    app.mainloop()
