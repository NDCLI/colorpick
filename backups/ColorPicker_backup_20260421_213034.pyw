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

# Auto-Update
try:
    from updater import check_for_updates
    HAS_UPDATER = True
except ImportError:
    HAS_UPDATER = False

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
# Dua tren bang mau tham chieu cua nguoi dung:
# Red, Orange, Yellow, Green, Blue, Purple,
# Pink, Brown, Gray, White, Black
# ==========================================

def single_instance_check():
    mutex_name = r"Global\ColorPicker_v2_Unique_Mutex"
    ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183:
        temp_root = ctk.CTk()
        temp_root.withdraw()
        messagebox.showinfo("Color Picker", "Ứng dụng đang chạy rồi bạn nhé!")
        sys.exit(0)

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(get_app_dir(), "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"topmost": False, "opacity": 1.0, "theme": "System", "auto_clipboard": True}

def save_settings(topmost, opacity, theme="System", auto_clipboard=True):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"topmost": topmost, "opacity": float(opacity),
                       "theme": theme, "auto_clipboard": auto_clipboard}, f)
    except:
        pass

# ==========================================
# DINH NGHIA 11 NHOM MAU
# Mau dai dien cho moi nhom (hex hien thi)
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
# Tinh toan tu mau dai dien cua tung nhom
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


def is_skin_tone(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h_deg = h * 360
    hue_match = (h_deg <= 28) or (h_deg >= 330)
    sat_match = (0.12 <= s <= 0.65)
    val_match = (0.3 <= v <= 1.0)
    return hue_match and sat_match and val_match


def detect_human_context(pixels):
    total = len(pixels)
    if total == 0:
        return False
    skin = sum(1 for p in pixels if is_skin_tone(tuple(p)))
    return 0.03 <= skin / total <= 0.45


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


# ==========================================
# CAC ENGINE PHAN TICH (ENSEMBLE)
# Moi engine tra ve 1 trong 11 ten nhom mau
# ==========================================

def engine_saliency(pixels):
    """Engine 1: Tinh toan mau noi bat nhat dua tren do bao hoa."""
    scores = collections.defaultdict(float)
    for p in pixels:
        name, sat = classify_pixel(tuple(p))
        # Chromatic colors get saturation boost; White gets neutral weight (not penalized)
        if name in ("Black",):
            weight = 0.5
        elif name in ("Gray",):
            weight = 0.75
        elif name == "White":
            weight = 1.0  # White is valid as primary, no penalty
        else:
            weight = 1.0 + sat * 2.0
        scores[name] += weight
    return max(scores, key=scores.get) if scores else "Gray"


def engine_frequency(pixels):
    """Engine 2: Mau xuat hien nhieu nhat (tan suat thuan tuy)."""
    counts = collections.Counter(classify_pixel(tuple(p))[0] for p in pixels)
    return counts.most_common(1)[0][0] if counts else "Gray"


def engine_core(image):
    """Engine 3: Tap trung phan tich 50% vung trung tam anh."""
    w, h = image.size
    cropped = image.crop((w * 0.25, h * 0.25, w * 0.75, h * 0.75))
    if cropped.mode == "RGBA":
        px = [tuple(p[:3]) for p in np.asarray(cropped).reshape(-1, 4) if p[3] > 0]
    else:
        px = np.asarray(cropped.convert("RGB")).reshape(-1, 3)
    if not len(px): return "Gray"
    return engine_saliency(px)


def engine_bg_remove(image):
    """Engine 4: Loai bo mau vien nen, tap trung mau chu the."""
    w, h = image.size
    edge = []
    is_rgba = (image.mode == "RGBA")
    img_data = image.load()
    for x in [0, w - 1]:
        for y in range(h):
            p = img_data[x, y]
            if not is_rgba or p[3] > 0: edge.append(p[:3] if is_rgba else p)
    for y in [0, h - 1]:
        for x in range(w):
            p = img_data[x, y]
            if not is_rgba or p[3] > 0: edge.append(p[:3] if is_rgba else p)

    if not edge:
        bg_name = "None"
    else:
        bg_name = collections.Counter(classify_pixel(tuple(p[:3]))[0] for p in edge).most_common(1)[0][0]

    scores = collections.defaultdict(float)
    if is_rgba:
        px = [tuple(p[:3]) for p in np.asarray(image).reshape(-1, 4) if p[3] > 0]
    else:
        px = np.asarray(image.convert("RGB")).reshape(-1, 3)
        
    for p in px:
        name, sat = classify_pixel(tuple(p))
        w_val = 0.3 if name == bg_name else (1.0 + sat * 2.0)
        scores[name] += w_val
    return max(scores, key=scores.get) if scores else "Gray"


def engine_kmeans(image, k=4, iterations=8):
    """Engine 5: K-Means clustering de tim cum mau chinh."""
    is_rgba = (image.mode == "RGBA")
    if is_rgba:
        px = np.array([p[:3] for p in np.asarray(image).reshape(-1, 4) if p[3] > 0], dtype=np.float32)
    else:
        px = np.asarray(image.convert("RGB"), dtype=np.float32).reshape(-1, 3)
        
    if len(px) == 0:
        return "Gray"

    sample = px[np.linspace(0, len(px) - 1, min(len(px), 2000), dtype=int)]
    k = max(1, min(k, len(sample)))
    centroids = sample[np.linspace(0, len(sample) - 1, k, dtype=int)].copy()

    labels = np.zeros(len(sample), dtype=int)
    for _ in range(iterations):
        dists = np.linalg.norm(sample[:, None] - centroids[None], axis=2)
        labels = np.argmin(dists, axis=1)
        for i in range(k):
            m = sample[labels == i]
            if len(m) > 0:
                centroids[i] = m.mean(axis=0)

    scores = collections.defaultdict(float)
    for i, c in enumerate(centroids):
        members = sample[labels == i]
        if len(members) == 0:
            continue
        name, sat = classify_pixel(tuple(int(x) for x in c))
        ratio = len(members) / len(sample)
        # White is no longer penalized; only Black/Gray get slight discount
        if name == "Black":
            penalty = 0.6
        elif name == "Gray":
            penalty = 0.8
        else:
            penalty = 1.0  # White and chromatic colors have full weight
        w_val = ratio * (1.0 + sat * 2.0) * penalty
        scores[name] += w_val

    return max(scores, key=scores.get) if scores else "Gray"


def engine_lab_expert(image):
    """Engine 6: So sanh mau trung binh anh voi bang mau chuan LAB/DeltaE."""
    is_rgba = (image.mode == "RGBA")
    if is_rgba:
        px = np.array([p[:3] for p in np.asarray(image).reshape(-1, 4) if p[3] > 0], dtype=np.float32)
    else:
        px = np.asarray(image.convert("RGB"), dtype=np.float32).reshape(-1, 3)
        
    if len(px) == 0:
        return "Gray"
    mean_rgb = tuple(int(round(v)) for v in px.mean(axis=0))
    mean_lab = rgb_to_lab(mean_rgb)

    best, best_dist = "Gray", float("inf")
    for name, ref in LAB_REFERENCE.items():
        d = delta_e(mean_lab, ref)
        if d < best_dist:
            best, best_dist = name, d
    return best


# ==========================================
# HE THONG BAU CHON ENSEMBLE
# ==========================================

def analyze_ensemble(image):
    """
    Phan tich anh bang 6 engine, bau chon ket qua.
    Tra ve danh sach dict: [{name, hex, confidence}, ...]
    """
    if image.mode != "RGBA":
        image = image.convert("RGB")
    thumb = image.copy()
    thumb.thumbnail((100, 100))
    if thumb.mode == "RGBA":
        px = np.array([p[:3] for p in np.asarray(thumb).reshape(-1, 4) if p[3] > 0])
    else:
        px = np.asarray(thumb).reshape(-1, 3)
        
    if len(px) == 0:
        return [{"name": "Black", "hex": "#1C1C1C", "confidence": 100}]

    # Thu phieu tu cac engine
    votes = [
        engine_saliency(px),
        engine_frequency(px),
        engine_core(thumb),
        engine_bg_remove(thumb),
        engine_kmeans(thumb),
        engine_lab_expert(thumb),
    ]

    vote_counts = collections.Counter(votes)
    winner, win_count = vote_counts.most_common(1)[0]
    # Neu chi co 1 phieu moi engine -> lay engine_saliency lam chuan
    final_color = winner if win_count >= 2 else votes[0]

    # Tinh do chinh xac cua ket qua chinh
    px_flat = [classify_pixel(tuple(p))[0] for p in px]
    px_counts = collections.Counter(px_flat)
    total_px = max(1, len(px_flat))

    final_px_share   = px_counts.get(final_color, 0) / total_px
    final_vote_share = vote_counts.get(final_color, 0) / len(votes)
    confidence = min(99, int(round((final_vote_share * 0.6 + final_px_share * 0.4) * 100)))

    # Tim cac mau phu (co the xuat hien song song)
    # 1. Dua tren tan suat pixel:
    #    - White/Gray: nguong thap hon (5%) vi de bi bo so voi mau co sac
    #    - Mau khac: nguong 10%
    secondary = []
    for name, cnt in px_counts.most_common():
        if name == final_color:
            continue
        ratio = cnt / total_px
        threshold = 0.05 if name in ("White", "Gray") else 0.10
        if ratio > threshold:
            secondary.append(name)
        if len(secondary) >= 2:
            break

    # 2. Dua tren LAB distance (neu co mau sat lai voi mau chinh)
    mean_arr = px.mean(axis=0)
    mean_rgb = (int(round(mean_arr[0])), int(round(mean_arr[1])), int(round(mean_arr[2])))
    mean_lab = rgb_to_lab(mean_rgb)

    dists = sorted((delta_e(mean_lab, ref), name) for name, ref in LAB_REFERENCE.items())
    for dist, name in dists[1:3]:  # Bo qua vi tri 0 (chinh no)
        if name != final_color and name not in secondary:
            if dists[0][0] > 0 and dist / dists[0][0] < 1.8:  # Khoang cach gan
                secondary.append(name)
            if len(secondary) >= 2:
                break

    secondary = secondary[:2]

    # Safety-net: if many near-white pixels exist but White is not captured,
    # force-inject White. Catches light pastel colors (e.g. light blue shirt)
    # that slip through classify_pixel with s just above threshold.
    if "White" != final_color and "White" not in secondary:
        near_white = 0
        for p in px:
            r_n = p[0] / 255.0
            g_n = p[1] / 255.0
            b_n = p[2] / 255.0
            v_px = max(r_n, g_n, b_n)
            s_px = (v_px - min(r_n, g_n, b_n)) / v_px if v_px > 0 else 0
            if v_px > 0.83 and s_px < 0.28:
                near_white += 1
        if near_white / total_px >= 0.12:
            secondary.insert(0, "White")
            secondary = secondary[:2]

    # Human context (emoji)
    is_human = detect_human_context(px)

    def display_name(name):
        if not is_human:
            return name
        hex_val = get_family_hex(name).lstrip("#")
        rgb_rep = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
        return f"👤 {name}" if is_skin_tone(rgb_rep) else f"👗 {name}"

    results = [{
        "name": display_name(final_color),
        "hex":  get_family_hex(final_color),
        "confidence": max(1, confidence)
    }]

    for i, sc in enumerate(secondary):
        sc_px  = px_counts.get(sc, 0) / total_px
        sc_vt  = vote_counts.get(sc, 0) / len(votes)
        cap    = 90 if i == 0 else 80
        sc_conf = min(cap, int(round((sc_vt * 0.55 + sc_px * 0.45) * 100)))
        results.append({
            "name": display_name(sc),
            "hex":  get_family_hex(sc),
            "confidence": max(1, sc_conf)
        })

    return results


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
# GIAO DIEN (UI) - KHONG THAY DOI LON
# ==========================================

def copy_hex(index):
    if index >= len(current_results):
        return
    app.clipboard_clear()
    app.clipboard_append(current_results[index]["hex"])
    app.update()
    status_dot.configure(fg_color="dodgerblue")


def get_image_signature(image):
    preview = image.convert("RGB").copy()
    preview.thumbnail((32, 32))
    return (image.size, preview.tobytes())


def load_clipboard_image():
    image = ImageGrab.grabclipboard()
    if isinstance(image, list) and len(image) > 0:
        image = Image.open(image[0])
    if image is None or not isinstance(image, Image.Image):
        return None
    return image.convert("RGB")


def render_analysis(image):
    global current_results
    image_frame.pack(before=result_container, pady=(5, 5))
    result_label1.configure(text="Loading...")
    result_label2.configure(text="")
    result_label3.configure(text="")
    result_confidence1.configure(text="")
    result_confidence2.configure(text="")
    result_confidence3.configure(text="")
    copy_btn1.pack_forget()
    copy_btn2.pack_forget()
    copy_btn3.pack_forget()
    status_dot.configure(fg_color="orange")
    app.update()

    def run_analysis():
        try:
            results = analyze_ensemble(image)
            app.after(0, lambda: finalize_render(image, results))
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            try:
                log_path = os.path.join(get_app_dir(), "error.log")
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(f"\n--- Analysis Error (v2.4) ---\n{err}\n")
            except Exception:
                pass
            app.after(0, lambda: status_dot.configure(fg_color="red"))
            app.after(0, lambda: result_label1.configure(text="Lỗi phân tích!"))

    threading.Thread(target=run_analysis, daemon=True).start()


def finalize_render(image, results):
    global current_results
    current_results = results

    color1 = results[0]
    result_color_box1.configure(fg_color=color1["hex"])
    result_label1.configure(text=color1["name"])
    result_confidence1.configure(text=f"{color1['confidence']}%")
    # copy_btn1.configure(text=f"Copy {color1['hex']}")
    # copy_btn1.pack(pady=(6, 0))

    if len(results) >= 2:
        color2 = results[1]
        result_color_box2.pack(before=result_label2, pady=2)
        result_color_box2.configure(fg_color=color2["hex"])
        result_label2.configure(text=color2["name"])
        result_confidence2.configure(text=f"{color2['confidence']}%")
        # copy_btn2.configure(text=f"Copy {color2['hex']}")
        # copy_btn2.pack(pady=(6, 0))
        color1_frame.pack_configure(side="left", expand=True)
        color2_frame.pack(side="left", expand=True, fill="both", padx=5)
    else:
        result_color_box2.pack_forget()
        result_label2.configure(text="")
        result_confidence2.configure(text="")
        copy_btn2.pack_forget()
        color1_frame.pack_configure(side="top", expand=True)
        color2_frame.pack_forget()

    if len(results) >= 3:
        color3 = results[2]
        result_color_box3.pack(before=result_label3, pady=2)
        result_color_box3.configure(fg_color=color3["hex"])
        result_label3.configure(text=color3["name"])
        result_confidence3.configure(text=f"{color3['confidence']}%")
        # copy_btn3.configure(text=f"Copy {color3['hex']}")
        # copy_btn3.pack(pady=(6, 0))
        color1_frame.pack_configure(side="left", expand=True)
        color3_frame.pack(side="left", expand=True, fill="both", padx=5)
    else:
        result_color_box3.pack_forget()
        result_label3.configure(text="")
        result_confidence3.configure(text="")
        copy_btn3.pack_forget()
        color3_frame.pack_forget()

    img_w, img_h = image.size
    ratio = min(150 / img_w, 150 / img_h)
    new_size = (int(img_w * ratio), int(img_h * ratio))
    ctk_img = ctk.CTkImage(light_image=image, dark_image=image, size=new_size)
    image_label.configure(image=ctk_img, text="")
    status_dot.configure(fg_color="green")


def analyze_clipboard_image(event=None):
    global last_clipboard_signature
    try:
        image = load_clipboard_image()
        if image is None:
            return
        last_clipboard_signature = get_image_signature(image)
        render_analysis(image)
    except Exception:
        status_dot.configure(fg_color="red")


def monitor_clipboard():
    global last_clipboard_signature
    if auto_clipboard_enabled:
        try:
            image = load_clipboard_image()
            if image is None:
                last_clipboard_signature = None
            else:
                sig = get_image_signature(image)
                if sig != last_clipboard_signature:
                    last_clipboard_signature = sig
                    render_analysis(image)
        except Exception:
            status_dot.configure(fg_color="red")
    app.after(1200, monitor_clipboard)


def toggle_pin():
    app.attributes("-topmost", pin_var.get())
    save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)


def change_opacity(value):
    global current_opacity
    current_opacity = float(value)
    app.attributes("-alpha", current_opacity)
    save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)
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
    sw.geometry("320x400")
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

    auto_cb_var = ctk.BooleanVar(value=auto_clipboard_enabled)

    def toggle_auto():
        global auto_clipboard_enabled
        auto_clipboard_enabled = auto_cb_var.get()
        save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)

    ctk.CTkSwitch(
        sw, text="📋 Tự động nhận ảnh từ Clipboard",
        variable=auto_cb_var, command=toggle_auto,
        font=ctk.CTkFont(size=13)
    ).pack(anchor="w", padx=20, pady=(0, 10))

    def set_theme(choice):
        global current_theme
        current_theme = choice
        ctk.set_appearance_mode(choice)
        save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)

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
    global current_results, last_clipboard_signature
    current_results = []
    last_clipboard_signature = None
    image_frame.pack_forget()
    image_label.configure(image="", text="")
    result_color_box1.configure(fg_color="gray")
    result_color_box2.pack_forget()
    result_color_box3.pack_forget()
    for lbl in [result_label1, result_label2, result_label3]:
        lbl.configure(text="")
    for lbl in [result_confidence1, result_confidence2, result_confidence3]:
        lbl.configure(text="")
    for btn in [copy_btn1, copy_btn2, copy_btn3]:
        btn.pack_forget()
    color1_frame.pack_configure(side="top", expand=True)
    color2_frame.pack_forget()
    color3_frame.pack_forget()
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

    # point_color_copy_btn.pack(pady=(4, 0))  # Hidden - click hex to copy
    point_color_frame.pack(pady=(2, 0), fill="x", padx=15)
    status_dot.configure(fg_color="#6366f1")


def copy_point_hex():
    if picked_point_color:
        app.clipboard_clear()
        app.clipboard_append(picked_point_color)
        app.update()
        status_dot.configure(fg_color="dodgerblue")


# ==========================================
# KHOI TAO UI
# ==========================================

picked_point_color = None
app_settings = load_settings()
current_opacity = app_settings.get("opacity", 1.0)
current_theme   = app_settings.get("theme", "System")
auto_clipboard_enabled = app_settings.get("auto_clipboard", True)

ctk.set_appearance_mode(current_theme)
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Color Picker v3.0")
app.geometry("360x310")
app.attributes("-alpha", current_opacity)
app.attributes("-topmost", app_settings.get("topmost", False))
app.minsize(340, 290)

# Top toolbar
top_frame = ctk.CTkFrame(app, fg_color="transparent")
top_frame.pack(fill="x", padx=15, pady=(10, 5))

pin_var = ctk.BooleanVar(value=app_settings.get("topmost", False))
ctk.CTkSwitch(top_frame, text="Ghim", variable=pin_var, command=toggle_pin).pack(side="left")

# --- KHOANH VUNG CHON DIEM MAU LASSO ---
lasso_active = False
lasso_overlay = None
lasso_canvas = None
lasso_points = []
lasso_screenshot = None
lasso_tk_img = None

def start_lasso():
    global lasso_active
    if lasso_active: return
    lasso_active = True
    app.withdraw()
    app.after(200, _launch_lasso)

def _launch_lasso():
    global lasso_overlay, lasso_canvas, lasso_screenshot, lasso_tk_img, lasso_points
    lasso_points = []
    try:
        lasso_screenshot = ImageGrab.grab()
    except Exception:
        cleanup_lasso()
        return

    enable_precision_mouse()
    
    scr_w = lasso_screenshot.width
    scr_h = lasso_screenshot.height

    overlay = tk.Toplevel()
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.geometry(f"{scr_w}x{scr_h}+0+0")
    lasso_overlay = overlay

    canvas = tk.Canvas(overlay, width=scr_w, height=scr_h, highlightthickness=0, cursor='crosshair')
    canvas.pack(fill="both", expand=True)
    lasso_canvas = canvas

    lasso_tk_img = ImageTk.PhotoImage(lasso_screenshot)
    canvas.create_image(0, 0, anchor="nw", image=lasso_tk_img)

    canvas.bind("<Button-1>", _lasso_on_click)
    canvas.bind("<B1-Motion>", _lasso_on_drag)
    canvas.bind("<ButtonRelease-1>", _lasso_on_release)
    canvas.bind("<Button-3>", _lasso_on_cancel)
    overlay.bind("<Escape>", _lasso_on_cancel)
    overlay.focus_force()

def _lasso_on_click(event):
    global lasso_points
    lasso_points = [(event.x, event.y)]

def _lasso_on_drag(event):
    global lasso_points
    if not lasso_points: return
    x, y = event.x, event.y
    px, py = lasso_points[-1]
    lasso_canvas.create_line(px, py, x, y, fill="#FF00FF", width=2, tags="lasso_line")
    lasso_points.append((x, y))

def _lasso_on_release(event):
    global lasso_points, lasso_screenshot
    if len(lasso_points) > 2:
        px, py = lasso_points[-1]
        fx, fy = lasso_points[0]
        lasso_canvas.create_line(px, py, fx, fy, fill="#FF00FF", width=2, tags="lasso_line")
        
        try:
            mask = Image.new('L', lasso_screenshot.size, 0)
            ImageDraw.Draw(mask).polygon(lasso_points, fill=255)
            
            rgba_img = lasso_screenshot.convert('RGBA')
            rgba_img.putalpha(mask)
            
            xs = [p[0] for p in lasso_points]
            ys = [p[1] for p in lasso_points]
            bbox = (min(xs), min(ys), max(xs), max(ys))
            cropped_img = rgba_img.crop(bbox)
            
            cleanup_lasso()
            render_analysis(cropped_img)
        except Exception as e:
            print(f"Lỗi: {e}")
            cleanup_lasso()
    else:
        cleanup_lasso()

def _lasso_on_cancel(event=None):
    cleanup_lasso()

def cleanup_lasso():
    global lasso_active, lasso_overlay, lasso_canvas, lasso_screenshot, lasso_tk_img
    restore_mouse_speed()
    lasso_active = False
    if lasso_overlay:
        try: lasso_overlay.destroy()
        except: pass
    lasso_overlay = lasso_canvas = lasso_screenshot = lasso_tk_img = None
    app.deiconify()
    app.lift()
    app.focus_force()

ctk.CTkButton(
    top_frame, text="🎯 Pick", width=80, height=26,
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

# Image preview
image_frame = ctk.CTkFrame(app, width=80, height=80, fg_color="gray20", corner_radius=12)
# image_frame.pack(pady=(5, 5))
image_frame.pack_propagate(False)
image_label = ctk.CTkLabel(image_frame, text="", text_color="gray60", font=ctk.CTkFont(size=11))
image_label.pack(expand=True, fill="both")

# Results area
result_container = ctk.CTkFrame(app, fg_color="transparent")
result_container.pack(pady=5, fill="x", padx=10)
current_results = []
last_clipboard_signature = None

color1_frame = ctk.CTkFrame(result_container, fg_color="transparent")
color1_frame.pack(side="top", expand=True)
result_color_box1 = ctk.CTkFrame(color1_frame, width=28, height=28, corner_radius=6, fg_color="gray")
result_color_box1.pack(pady=1)
result_label1 = ctk.CTkLabel(color1_frame, text="", font=ctk.CTkFont(size=15, weight="bold"))
result_label1.pack()
result_confidence1 = ctk.CTkLabel(color1_frame, text="", text_color="gray70", font=ctk.CTkFont(size=11))
result_confidence1.pack()
copy_btn1 = ctk.CTkButton(color1_frame, text="Copy HEX", width=80, height=22,
                           font=ctk.CTkFont(size=10), command=lambda: copy_hex(0))

color2_frame = ctk.CTkFrame(result_container, fg_color="transparent")
result_color_box2 = ctk.CTkFrame(color2_frame, width=28, height=28, corner_radius=6, fg_color="transparent")
result_color_box2.pack(pady=1)
result_label2 = ctk.CTkLabel(color2_frame, text="", font=ctk.CTkFont(size=15, weight="bold"))
result_label2.pack()
result_confidence2 = ctk.CTkLabel(color2_frame, text="", text_color="gray70", font=ctk.CTkFont(size=11))
result_confidence2.pack()
copy_btn2 = ctk.CTkButton(color2_frame, text="Copy HEX", width=80, height=22,
                           font=ctk.CTkFont(size=10), command=lambda: copy_hex(1))

color3_frame = ctk.CTkFrame(result_container, fg_color="transparent")
result_color_box3 = ctk.CTkFrame(color3_frame, width=28, height=28, corner_radius=6, fg_color="transparent")
result_color_box3.pack(pady=1)
result_label3 = ctk.CTkLabel(color3_frame, text="", font=ctk.CTkFont(size=15, weight="bold"))
result_label3.pack()
result_confidence3 = ctk.CTkLabel(color3_frame, text="", text_color="gray70", font=ctk.CTkFont(size=11))
result_confidence3.pack()
copy_btn3 = ctk.CTkButton(color3_frame, text="Copy HEX", width=80, height=22,
                           font=ctk.CTkFont(size=10), command=lambda: copy_hex(2))

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

point_color_copy_btn = ctk.CTkButton(
    point_color_frame, text="Copy HEX", width=80, height=22,
    fg_color="#6366f1", hover_color="#4f46e5", font=ctk.CTkFont(size=10),
    command=copy_point_hex
)
# point_color_copy_btn.pack(pady=(5, 0))  # Hidden - click hex to copy

status_dot = ctk.CTkFrame(app, width=10, height=10, corner_radius=5, fg_color="green")
# status_dot.pack(pady=10, side="bottom")  # Hidden - compact UI

update_status_label = ctk.CTkLabel(
    app, text="", 
    font=ctk.CTkFont(size=10), 
    text_color="gray50",
    height=15
)
update_status_label.pack(side="bottom", pady=(0, 2))

app.bind("<Control-v>", analyze_clipboard_image)
app.bind("<Control-V>", analyze_clipboard_image)
app.after(1200, monitor_clipboard)

# ==========================================
# WIN32 HOTKEY LISTENER (Alt+S / Alt+A)
# ==========================================

def start_hotkey_listener():
    def listener():
        user32 = ctypes.windll.user32
        MOD_ALT = 0x0001
        VK_S = 0x53
        VK_A = 0x41
        user32.RegisterHotKey(None, 1, MOD_ALT, VK_S)
        user32.RegisterHotKey(None, 3, MOD_ALT, VK_A)
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:
                    if msg.wParam == 1:
                        app.after(0, start_eyedropper)
                    elif msg.wParam == 3:
                        app.after(0, start_lasso)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
            user32.UnregisterHotKey(None, 3)

    threading.Thread(target=listener, daemon=True).start()


def update_ui_with_status(msg):
    """Callback để cập nhật trạng thái lên UI từ thread khác"""
    def _update():
        if app.winfo_exists():
            update_status_label.configure(text=msg)
            # Tự động xóa thông báo sau 5 giây nếu không phải đang tải/cập nhật
            if any(x in msg for x in ["mới nhất", "❌", "⚠️", "Đã hủy", "thành công"]):
                app.after(5000, lambda: update_status_label.configure(text="") if update_status_label.winfo_exists() else None)
    
    app.after(0, _update)


if __name__ == "__main__":
    single_instance_check()
    start_hotkey_listener()
    
    # Kiểm tra cập nhật trong thread riêng (với callback UI)
    if HAS_UPDATER:
        threading.Thread(target=check_for_updates, args=(update_ui_with_status,), daemon=True).start()
    
    app.mainloop()
