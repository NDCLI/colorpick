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
import math
import threading
try:
    import keyboard
except ImportError:
    keyboard = None

# DPI Awareness cho Windows - dam bao chup man hinh chinh xac
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# v2.0 - HỆ THỐNG HỘI ĐỒNG AI (ENSEMBLE VOTING)

def single_instance_check():
    """Windows Mutex"""
    mutex_name = r"Global\ColorPicker_v2_Unique_Mutex"
    # CreateMutexW(lpMutexAttributes, bInitialOwner, lpName)
    ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
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

# --- DINH NGHIA MAU SAC ---

BASIC_COLORS = {
    "Red": (255, 0, 0), "Green": (0, 255, 0), "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0), "Orange": (255, 165, 0), "Purple": (128, 0, 128),
    "Pink": (255, 192, 203), "Brown": (165, 42, 42), "Black": (0, 0, 0),
    "White": (255, 255, 255), "Gray": (128, 128, 128), "Cyan": (0, 255, 255)
}

COLOR_HEX = {
    "Red (Ruby)": "#9B111E",
    "Red (Classic)": "#FF0000",
    "Red (Burgundy)": "#800020",
    "Red (Mahogany)": "#C04000",
    "Red (Raspberry)": "#B3446C",
    "Red (Blood)": "#8A0707",
    "Red (Crimson)": "#DC143C",
    "Red (Maroon)": "#800000",
    "Red (Terracotta)": "#E35336",
    "Red (Chilli)": "#CD1C18",
    "Red (Strawberry)": "#D53032",
    "Red (Scarlet)": "#FF2400",
    "Red (Obsidian)": "#390E19",
    "Red (Dark Berry)": "#750134",
    "Red (Blood Deep)": "#480608",
    "Orange (Gold)": "#FFD700",
    "Orange (Mango)": "#F4BB44",
    "Orange (Salamander)": "#EF4F1B",
    "Orange (Burnt)": "#E55529",
    "Orange (Salmon)": "#FA8766",
    "Orange (Melon)": "#FDBCB4",
    "Orange (Coral)": "#FF7F50",
    "Orange (Saffron)": "#F4C430",
    "Orange (Apricot)": "#FBCEB1",
    "Orange (Amber)": "#FFBF00",
    "Orange (Bright)": "#FF8C00",
    "Orange (Carrot)": "#ED9121",
    "Orange (Pumpkin)": "#FF7518",
    "Orange (Honey)": "#EBA937",
    "Green (Jade)": "#00A86B",
    "Green (Army)": "#4B5320",
    "Green (Forest)": "#228B22",
    "Green (Lime)": "#BFFF00",
    "Green (Hunter)": "#355E3B",
    "Green (Dark)": "#006400",
    "Green (Apple)": "#8DB600",
    "Green (Mint)": "#98FF98",
    "Green (Olive)": "#808000",
    "Green (Pine)": "#01796F",
    "Green (Pastel)": "#77DD77",
    "Green (Emerald)": "#50C878",
    "Green (Pale)": "#DAEDBB",
    "Green (Olive)": "#989B5D",
    "Green (Moss)": "#817E26",
    "Yellow (Mimosa)": "#FFCA4B",
    "Yellow (Pastel)": "#FFFFBA",
    "Yellow (Lemon)": "#FFF44F",
    "Yellow (Neon)": "#FFFF33",
    "Yellow (Sunflower)": "#FFDA03",
    "Yellow (Tuscany)": "#FAD6A5",
    "Yellow (Canary)": "#FFFF8F",
    "Yellow (Classic)": "#FFF44F",
    "Yellow (Sunshine)": "#FFFD37",
    "Yellow (Illuminating)": "#F5DF4D",
    "Yellow (Bumblebee)": "#F7CE4C",
    "Yellow (Bright)": "#FFEA00",
    "Yellow (Canary)": "#F4EF50",
    "Yellow (Lime)": "#D5F42D",
    "Yellow (Neon Soft)": "#F1F523",
    "Yellow (Pale Sun)": "#FFF465",
    "Yellow (Bright Pure)": "#FFF40D",
    "Yellow (Sand)": "#D6C09D",
    "Blue (Cyan)": "#00FFFF",
    "Blue (Navy)": "#000080",
    "Blue (Turquoise)": "#40E0D0",
    "Blue (Aqua)": "#00FFFF",
    "Blue (Royal)": "#4169E1",
    "Blue (Sapphire)": "#0F52BA",
    "Blue (Sky)": "#87CEEB",
    "Blue (Egyptian)": "#1034A6",
    "Blue (Azure)": "#007FFF",
    "Blue (Baby)": "#89CFF0",
    "Blue (Classic)": "#0F4C81",
    "Blue (Space)": "#1C39BB",
    "Purple (Lavender)": "#E6E6FA",
    "Purple (Violet)": "#8F00FF",
    "Purple (Amethyst)": "#9966CC",
    "Purple (Eggplant)": "#614051",
    "Purple (Royal)": "#7851A9",
    "Purple (Lilac)": "#C8A2C8",
    "Purple (Iris)": "#5A4FCF",
    "Purple (Bright)": "#BF00FF",
    "Purple (Wine)": "#722F37",
    "Purple (Light)": "#E0B0FF",
    "Purple (Psychedelic)": "#DF00FF",
    "Purple (Plum)": "#8E4585",
    "Purple (Muted)": "#6F6691",
    "Purple (Deep)": "#5D448D",
    "Purple (Soft)": "#F4E5F8",
    "Purple (Pale Frost)": "#F6E4FC",
    "Pink (Fuchsia)": "#FF00FF",
    "Pink (Dusty)": "#BD96A8",
    "Pink (Rose)": "#FF007F",
    "Pink (Flamingo)": "#FC8EAC",
    "Pink (Coral)": "#F88379",
    "Pink (Bright)": "#FF007F",
    "Pink (Peach)": "#FFE5B4",
    "Pink (Neon)": "#FF6EC7",
    "Pink (Hot)": "#FF69B4",
    "Pink (Light)": "#FFB6C1",
    "Pink (Orchid)": "#DA70D6",
    "Pink (Baby)": "#F4C2C2",
    "Pink (Doll)": "#F2B8C6",
    "Pink (Rose Light)": "#F7A5B5",
    "Pink (Bubblegum)": "#FD94B7",
    "Pink (Coral Red)": "#FE6477",
    "Pink (Peach Glow)": "#FEBDAB",
    "Pink (Magenta)": "#EE2DFF",
    "Pink (Hot Deep)": "#E90EAA",
    "Pink (Electric)": "#EB0DAC",
    "Pink (Soft Mist)": "#FDD3E8",
    "Pink (Candy)": "#FFAACF",
    "Pink (Deep Rose)": "#E44895",
    "Brown (Bronze)": "#CD7F32",
    "Brown (Cinnamon)": "#D2691E",
    "Brown (Brunette)": "#4A2C2A",
    "Brown (Coffee)": "#6F4E37",
    "Brown (Peanut)": "#795C34",
    "Brown (Walnut)": "#59392B",
    "Brown (Wood)": "#966919",
    "Brown (Dark)": "#3D2B1F",
    "Brown (Rustic)": "#4C2E28",
    "Brown (Chocolate)": "#7B3F00",
    "Brown (Wenge)": "#645452",
    "Brown (Chestnut)": "#954535",
    "Brown (Sand)": "#C2B280",
    "Brown (Earth)": "#AB5926",
    "Brown (Sandy)": "#B9733A",
    "Brown (Almond)": "#DEC3A3",
    "Brown (Caramel)": "#CA8938",
    "White (Rice)": "#FAF9F6",
    "White (Bone)": "#F9F6EE",
    "White (Powder)": "#FEFEFA",
    "White (Pearl)": "#F0EAD6",
    "White (Ivory)": "#FFFFF0",
    "White (Cream)": "#FFFDD0",
    "White (Snow)": "#FFFAFA",
    "White (Lace)": "#FDF5E6",
    "White (Cotton)": "#FBFBF9",
    "White (Linen)": "#FAF0E6",
    "White (Coconut)": "#FFFFFF",
    "White (Porcelain)": "#FCF8F4",
    "Gray (Silver)": "#C0C0C0",
    "Gray (Smoke)": "#738276",
    "Gray (Charcoal)": "#36454F",
    "Gray (Mouse)": "#96918F",
    "Gray (Iron)": "#48494B",
    "Gray (Dolphin)": "#828E84",
    "Gray (Steel)": "#777B7E",
    "Gray (Dove)": "#6D6C6C",
    "Gray (Rhino)": "#B9BBB6",
    "Gray (Graphite)": "#383838",
    "Gray (Cool)": "#8C92AC",
    "Gray (Pale)": "#D1D0CE",
    "Black (Ebony)": "#555D50",
    "Black (Smokey)": "#100C08",
    "Black (Charcoal)": "#333333",
    "Black (Ink)": "#070304",
    "Black (Carbon)": "#333333",
    "Black (Rich)": "#010B13",
    "Black (Graphite)": "#232222",
    "Black (Midnight)": "#191970",
    "Black (Oil)": "#281E15",
    "Black (Onyx)": "#353935",
    "Black (Space)": "#1C253C",
    "Black (Coal)": "#151716",
    "Black (Night)": "#333335",
    "Black (Abyss)": "#323234",
    "Black (Obsidian Deep)": "#5E5E5E",
    "Black (True Charcoal)": "#333333",
}

LAB_REFERENCE = {
    "Red (Ruby)": (32.84, 53.25, 32.03),
    "Red (Classic)": (53.23, 80.11, 67.22),
    "Red (Burgundy)": (25.84, 48.9, 21.29),
    "Red (Mahogany)": (45.46, 49.22, 56.69),
    "Red (Raspberry)": (45.36, 48.73, 0.67),
    "Red (Blood)": (28.3, 49.68, 38.53),
    "Red (Crimson)": (47.03, 70.94, 33.59),
    "Red (Maroon)": (25.53, 48.06, 38.06),
    "Red (Terracotta)": (54.85, 54.49, 45.96),
    "Red (Chilli)": (44.05, 64.71, 49.19),
    "Red (Strawberry)": (47.61, 62.7, 39.68),
    "Red (Scarlet)": (54.58, 76.24, 67.71),
    "Red (Obsidian)": (10.95, 22.33, 3.82),
    "Red (Dark Berry)": (23.84, 47.09, 4.44),
    "Red (Blood Deep)": (12.77, 30.07, 16.62),
    "Orange (Gold)": (86.93, -1.92, 87.14),
    "Orange (Mango)": (79.15, 9.34, 65.16),
    "Orange (Salamander)": (56.11, 59.42, 59.9),
    "Orange (Burnt)": (55.4, 53.9, 52.92),
    "Orange (Salmon)": (68.47, 40.84, 37.18),
    "Orange (Melon)": (81.92, 22.33, 13.22),
    "Orange (Coral)": (67.29, 45.36, 47.49),
    "Orange (Saffron)": (81.25, 3.89, 74.15),
    "Orange (Apricot)": (85.92, 11.78, 20.39),
    "Orange (Amber)": (81.03, 10.39, 83.04),
    "Orange (Bright)": (69.48, 36.83, 75.49),
    "Orange (Carrot)": (68.29, 27.32, 67.34),
    "Orange (Pumpkin)": (65.0, 48.38, 68.43),
    "Orange (Honey)": (73.75, 14.45, 64.61),
    "Green (Jade)": (60.84, -51.41, 21.43),
    "Green (Army)": (33.53, -11.64, 28.26),
    "Green (Forest)": (50.59, -49.59, 45.02),
    "Green (Lime)": (92.84, -46.87, 89.36),
    "Green (Hunter)": (36.13, -22.79, 15.69),
    "Green (Dark)": (36.2, -43.37, 41.86),
    "Green (Apple)": (68.84, -34.13, 69.78),
    "Green (Mint)": (91.89, -49.98, 40.01),
    "Green (Olive)": (51.87, -12.93, 56.68),
    "Green (Pine)": (45.4, -30.84, -2.65),
    "Green (Pastel)": (80.16, -50.08, 40.91),
    "Green (Emerald)": (72.48, -51.25, 30.25),
    "Green (Pale)": (91.26, -14.78, 22.18),
    "Green (Olive)": (62.43, -10.82, 32.12),
    "Green (Moss)": (51.53, -10.11, 46.01),
    "Yellow (Mimosa)": (83.97, 6.49, 67.58),
    "Yellow (Pastel)": (98.56, -10.45, 33.08),
    "Yellow (Lemon)": (94.54, -14.41, 76.62),
    "Yellow (Neon)": (97.24, -20.77, 87.55),
    "Yellow (Sunflower)": (87.68, -3.42, 87.42),
    "Yellow (Tuscany)": (87.55, 5.76, 28.87),
    "Yellow (Canary)": (97.94, -15.21, 53.26),
    "Yellow (Classic)": (94.54, -14.41, 76.62),
    "Yellow (Sunshine)": (96.73, -19.7, 86.11),
    "Yellow (Illuminating)": (88.32, -8.26, 70.88),
    "Yellow (Bumblebee)": (84.19, 1.14, 67.16),
    "Yellow (Bright)": (91.73, -11.41, 90.56),
    "Yellow (Canary)": (92.37, -16.41, 73.81),
    "Yellow (Lime)": (91.25, -32.74, 82.64),
    "Yellow (Neon Soft)": (93.51, -22.13, 87.43),
    "Yellow (Pale Sun)": (94.7, -13.18, 68.25),
    "Yellow (Bright Pure)": (94.31, -16.19, 91.46),
    "Yellow (Sand)": (78.71, 2.44, 20.5),
    "Blue (Cyan)": (91.12, -48.08, -14.14),
    "Blue (Navy)": (12.98, 47.51, -64.7),
    "Blue (Turquoise)": (81.27, -44.08, -4.03),
    "Blue (Aqua)": (91.12, -48.08, -14.14),
    "Blue (Royal)": (47.83, 26.27, -65.27),
    "Blue (Sapphire)": (37.26, 21.78, -60.05),
    "Blue (Sky)": (79.21, -14.83, -21.28),
    "Blue (Egyptian)": (27.63, 34.0, -63.93),
    "Blue (Azure)": (54.45, 19.41, -71.36),
    "Blue (Baby)": (79.75, -13.55, -23.13),
    "Blue (Classic)": (31.48, 2.36, -35.03),
    "Blue (Space)": (31.26, 39.32, -70.47),
    "Purple (Lavender)": (91.83, 3.71, -9.67),
    "Purple (Violet)": (42.85, 84.39, -90.03),
    "Purple (Amethyst)": (52.55, 40.32, -45.41),
    "Purple (Eggplant)": (31.35, 17.26, -4.38),
    "Purple (Royal)": (42.37, 34.72, -41.46),
    "Purple (Lilac)": (71.07, 20.55, -14.14),
    "Purple (Iris)": (41.64, 40.12, -64.98),
    "Purple (Bright)": (49.85, 89.39, -78.27),
    "Purple (Wine)": (29.12, 30.37, 9.72),
    "Purple (Light)": (78.53, 31.51, -32.49),
    "Purple (Psychedelic)": (54.98, 93.56, -69.72),
    "Purple (Plum)": (40.74, 39.99, -22.19),
    "Purple (Muted)": (45.53, 13.23, -22.3),
    "Purple (Deep)": (34.77, 27.66, -36.89),
    "Purple (Soft)": (92.6, 8.42, -7.37),
    "Purple (Pale Frost)": (92.62, 10.33, -9.4),
    "Pink (Fuchsia)": (60.32, 98.25, -60.84),
    "Pink (Dusty)": (66.1, 17.52, -3.84),
    "Pink (Rose)": (54.86, 84.48, 4.63),
    "Pink (Flamingo)": (71.57, 44.85, 2.76),
    "Pink (Coral)": (67.7, 43.59, 25.74),
    "Pink (Bright)": (54.86, 84.48, 4.63),
    "Pink (Peach)": (91.95, 1.81, 27.18),
    "Pink (Neon)": (66.93, 64.51, -19.22),
    "Pink (Hot)": (65.48, 64.25, -10.66),
    "Pink (Light)": (81.05, 27.97, 5.03),
    "Pink (Orchid)": (62.8, 55.29, -34.42),
    "Pink (Baby)": (82.76, 17.83, 6.81),
    "Pink (Doll)": (80.31, 23.0, 1.09),
    "Pink (Rose Light)": (76.08, 32.38, 4.26),
    "Pink (Bubblegum)": (73.21, 43.55, -0.94),
    "Pink (Coral Red)": (62.94, 60.0, 20.61),
    "Pink (Peach Glow)": (82.06, 21.04, 18.25),
    "Pink (Magenta)": (59.23, 90.5, -62.75),
    "Pink (Hot Deep)": (52.44, 82.83, -25.04),
    "Pink (Electric)": (52.87, 83.53, -25.52),
    "Pink (Soft Mist)": (88.59, 18.04, -4.81),
    "Pink (Candy)": (78.76, 36.26, -5.91),
    "Pink (Deep Rose)": (55.38, 66.21, -8.27),
    "Brown (Bronze)": (60.24, 24.02, 52.33),
    "Brown (Cinnamon)": (55.99, 37.06, 56.74),
    "Brown (Brunette)": (21.67, 13.59, 7.11),
    "Brown (Coffee)": (36.18, 10.87, 19.09),
    "Brown (Peanut)": (41.16, 6.73, 27.38),
    "Brown (Walnut)": (27.37, 12.38, 14.52),
    "Brown (Wood)": (47.83, 10.98, 48.35),
    "Brown (Dark)": (19.3, 6.47, 11.07),
    "Brown (Rustic)": (22.46, 12.96, 9.6),
    "Brown (Chocolate)": (33.49, 22.29, 43.8),
    "Brown (Wenge)": (37.22, 6.23, 3.61),
    "Brown (Chestnut)": (39.42, 32.33, 25.52),
    "Brown (Sand)": (72.81, -1.75, 27.67),
    "Brown (Earth)": (46.9, 29.79, 42.98),
    "Brown (Sandy)": (54.95, 22.47, 42.2),
    "Brown (Almond)": (80.29, 4.73, 19.6),
    "Brown (Caramel)": (62.28, 17.57, 51.62),
    "White (Rice)": (97.93, -0.19, 1.54),
    "White (Bone)": (96.91, -0.37, 4.18),
    "White (Powder)": (99.56, -0.69, 1.9),
    "White (Pearl)": (92.67, -1.32, 10.42),
    "White (Ivory)": (99.64, -2.55, 7.15),
    "White (Cream)": (98.46, -6.49, 21.82),
    "White (Snow)": (98.64, 1.66, 0.58),
    "White (Lace)": (96.78, 0.18, 8.16),
    "White (Cotton)": (98.57, -0.34, 0.95),
    "White (Linen)": (95.31, 1.68, 6.01),
    "White (Coconut)": (100.0, 0.01, -0.01),
    "White (Porcelain)": (97.78, 0.64, 2.38),
    "Gray (Silver)": (77.7, 0.0, -0.01),
    "Gray (Smoke)": (52.86, -7.97, 4.64),
    "Gray (Charcoal)": (28.39, -3.25, -7.96),
    "Gray (Mouse)": (60.53, 1.47, 1.71),
    "Gray (Iron)": (31.0, 0.04, -1.34),
    "Gray (Dolphin)": (57.81, -6.36, 3.83),
    "Gray (Steel)": (51.38, -0.87, -2.16),
    "Gray (Dove)": (45.71, 0.39, 0.13),
    "Gray (Rhino)": (75.6, -1.62, 2.27),
    "Gray (Graphite)": (23.52, 0.0, -0.0),
    "Gray (Cool)": (60.88, 3.44, -14.35),
    "Gray (Pale)": (83.51, -0.01, 1.1),
    "Black (Ebony)": (38.44, -5.86, 6.41),
    "Black (Smokey)": (3.53, 0.73, 2.01),
    "Black (Charcoal)": (21.25, 0.0, -0.0),
    "Black (Ink)": (1.08, 1.19, -0.01),
    "Black (Carbon)": (21.25, 0.0, -0.0),
    "Black (Rich)": (2.64, -1.17, -4.87),
    "Black (Graphite)": (13.33, 0.47, 0.16),
    "Black (Midnight)": (15.86, 31.72, -49.58),
    "Black (Oil)": (12.18, 3.24, 8.01),
    "Black (Onyx)": (23.47, -2.63, 1.9),
    "Black (Space)": (14.93, 3.69, -16.01),
    "Black (Coal)": (7.5, -1.17, 0.35),
    "Black (Night)": (21.31, 0.47, -1.27),
    "Black (Abyss)": (20.86, 0.48, -1.27),
    "Black (Obsidian Deep)": (39.9, 0.0, -0.01),
    "Black (True Charcoal)": (21.25, 0.0, -0.0),
}


def classify_pixel_hsv(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h_deg = h * 360
    if v < 0.42: return "Black (Carbon)", s
    if v > 0.82 and s < 0.06: return "White (Coconut)", s
    if s < 0.15: return "Gray (Silver)", s 
    if h_deg < 10 or h_deg >= 330: 
        res = "Brown (Dark)" if v < 0.1 else "Red (Classic)"
    elif 10 <= h_deg < 42: 
        res = "Brown (Dark)" if (v < 0.82 and s < 0.78) or (v < 0.6) else "Orange (Bright)"
    elif 42 <= h_deg < 75: res = "Yellow (Bright)"
    elif 75 <= h_deg < 165: res = "Green (Emerald)"
    elif 165 <= h_deg < 205: res = "Blue (Cyan)"
    elif 205 <= h_deg < 245: res = "Blue (Classic)"
    elif 245 <= h_deg < 290: res = "Purple (Violet)"
    else: res = "Pink (Fuchsia)"
    return res, s

def is_skin_tone(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h_deg = h * 360
    # Range xac dinh da nguoi (Skin Tone heuristic)
    hue_match = (h_deg <= 28) or (h_deg >= 330)
    sat_match = (0.12 <= s <= 0.65)
    val_match = (0.3 <= v <= 1.0)
    return hue_match and sat_match and val_match

def detect_human_context(pixels):
    """Kiem tra xem anh co phai la anh nguoi/toan than hay khong"""
    total_pixels = len(pixels)
    if total_pixels == 0: return False
    
    skin_pixels = sum(1 for p in pixels if is_skin_tone(tuple(p)))
    skin_ratio = skin_pixels / total_pixels
    
    # Heuristic: Anh nguoi thuong co tu 3% den 45% la da
    return 0.03 <= skin_ratio <= 0.45

def rgb_to_lab(rgb):
    def pivot_rgb(value):
        value = value / 255.0
        return ((value + 0.055) / 1.055) ** 2.4 if value > 0.04045 else value / 12.92

    def pivot_xyz(value):
        return value ** (1 / 3) if value > 0.008856 else (7.787 * value) + (16 / 116)

    r, g, b = (pivot_rgb(channel) for channel in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    fx, fy, fz = pivot_xyz(x), pivot_xyz(y), pivot_xyz(z)
    l = max(0.0, (116 * fy) - 16)
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return (l, a, b_val)

def delta_e(lab_a, lab_b):
    return sum((left - right) ** 2 for left, right in zip(lab_a, lab_b)) ** 0.5

# --- CAC ENGINE CHUYEN GIA ---

def engine_saliency(pixels):
    """Heuristic v1.3"""
    scores = collections.defaultdict(float)
    for p in pixels:
        name, sat = classify_pixel_hsv(p)
        weight = 1.0 if name in ["Black (Carbon)", "White (Coconut)", "Gray (Silver)"] else (1.0 + sat * 1.5)
        scores[name] += weight
    return max(scores, key=scores.get) if scores else None

def engine_most_frequent(pixels):
    """Engine 2: UU tien so luong thuan tuy"""
    counts = collections.Counter([classify_pixel_hsv(p)[0] for p in pixels])
    return counts.most_common(1)[0][0] if counts else None

def engine_core_focus(image):
    """Engine 3: Tap trung vao 50% vung trung tam"""
    w, h = image.size
    left, top, right, bottom = w*0.25, h*0.25, w*0.75, h*0.75
    core_img = image.crop((left, top, right, bottom))
    core_pixels = np.asarray(core_img.convert('RGB'))
    return engine_saliency(core_pixels.reshape(-1, 3))

def engine_bg_purger(image):
    """Engine 4: Tu dong loai bo mau nen o ria anh"""
    w, h = image.size
    # Lay mau o 4 goc va ria
    edge_pixels = []
    for x in [0, w-1]:
        for y in range(h): edge_pixels.append(image.getpixel((x, y)))
    for y in [0, h-1]:
        for x in range(w): edge_pixels.append(image.getpixel((x, y)))
    
    bg_counts = collections.Counter([classify_pixel_hsv(p)[0] for p in edge_pixels])
    bg_color = bg_counts.most_common(1)[0][0]
    
    # Loc pixels trong anh, giam diem mau nen
    pixels = np.asarray(image.convert('RGB')).reshape(-1, 3)
    scores = collections.defaultdict(float)
    for p in pixels:
        name, sat = classify_pixel_hsv(p)
        weight = 0.5 if name == bg_color else (1.0 + sat * 1.5)
        scores[name] += weight
    return max(scores, key=scores.get) if scores else None

def engine_palette_cluster(image, clusters=4, iterations=6):
    """Engine 5: Phan cum bang K-Means de tim mau chu dao"""
    rgb_image = image.convert("RGB")
    pixels = np.asarray(rgb_image, dtype=np.float32).reshape(-1, 3)
    if len(pixels) == 0:
        return None

    sample_size = min(len(pixels), 2500)
    if len(pixels) > sample_size:
        indices = np.linspace(0, len(pixels) - 1, sample_size, dtype=int)
        sample = pixels[indices]
    else:
        sample = pixels

    k = max(1, min(clusters, len(sample)))
    seeds = np.linspace(0, len(sample) - 1, k, dtype=int)
    centroids = sample[seeds].copy()

    for _ in range(iterations):
        distances = np.linalg.norm(sample[:, None, :] - centroids[None, :, :], axis=2)
        labels = np.argmin(distances, axis=1)
        new_centroids = centroids.copy()
        for idx in range(k):
            members = sample[labels == idx]
            if len(members) > 0:
                new_centroids[idx] = members.mean(axis=0)
        if np.allclose(new_centroids, centroids):
            break
        centroids = new_centroids

    scores = collections.defaultdict(float)
    for idx, centroid in enumerate(centroids):
        members = sample[labels == idx]
        if len(members) == 0:
            continue

        centroid_rgb = tuple(int(max(0, min(255, round(v)))) for v in centroid)
        name, sat = classify_pixel_hsv(centroid_rgb)
        cluster_ratio = len(members) / len(sample)
        neutral_penalty = 0.6 if name in ["Black (Carbon)", "White (Coconut)", "Gray (Silver)"] else 1.0
        scores[name] += cluster_ratio * (1.0 + sat * 1.8) * neutral_penalty

    return max(scores, key=scores.get) if scores else None

def engine_lab_distance(image):
    """Engine 6: So mau trung binh voi bang mau tham chieu bang LAB/Delta E"""
    rgb_image = image.convert("RGB")
    pixels = np.asarray(rgb_image, dtype=np.float32).reshape(-1, 3)
    if len(pixels) == 0:
        return None

    mean_rgb = tuple(int(round(value)) for value in pixels.mean(axis=0))
    mean_lab = rgb_to_lab(mean_rgb)

    best_name = None
    best_distance = None
    for color_name, reference_lab in LAB_REFERENCE.items():
        distance = delta_e(mean_lab, reference_lab)
        if best_distance is None or distance < best_distance:
            best_name = color_name
            best_distance = distance

    return best_name

# --- HE THONG BAU CHON (ENSEMBLE) ---

def analyze_ensemble(image):
    image_thumb = image.convert('RGB')
    image_thumb.thumbnail((100, 100))
    pixels = np.asarray(image_thumb).reshape(-1, 3)
    
    # Thu thap ket qua tu cac chuyen gia
    votes = []
    votes.append(engine_saliency(pixels))
    votes.append(engine_most_frequent(pixels))
    votes.append(engine_core_focus(image_thumb))
    votes.append(engine_bg_purger(image_thumb))
    votes.append(engine_palette_cluster(image_thumb))
    votes.append(engine_lab_distance(image_thumb))
    
    # Dem phieu
    vote_counts = collections.Counter(votes)
    winner, win_count = vote_counts.most_common(1)[0]
    
    # He thong uu tien:
    # 1. Neu co 2 AI tro len dong y -> Lay mau do
    # 2. Neu moi AI 1 phieu (chia re) -> Lay ket qua cua Saliency (votes[0])
    final_color = winner if win_count >= 2 else votes[0]
    
    # Tim top mau phu dua tren tan suat pixel
    pixels_flat = [classify_pixel_hsv(tuple(p))[0] for p in pixels]
    counts = collections.Counter(pixels_flat)
    all_colors = counts.most_common(3)
    secondary_colors = []
    for name, count in all_colors:
        if name != final_color and count > (len(pixels) * 0.08):
            secondary_colors.append(name)
        if len(secondary_colors) == 2:
            break

    final_pixel_share = counts.get(final_color, 0) / max(1, len(pixels))
    final_vote_share = vote_counts.get(final_color, 0) / max(1, len(votes))
    final_confidence = min(99, int(round((final_vote_share * 0.65 + final_pixel_share * 0.35) * 100)))

    # --- HUMAN DETECTION LOGIC ---
    is_human = detect_human_context(pixels)
    
    def get_display_name(color_name, is_human_ctx):
        if not is_human_ctx:
            return color_name
        
        # Lay RGB tu COLOR_HEX
        h_hex = COLOR_HEX[color_name].lstrip('#')
        rgb = tuple(int(h_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Lay ten mau rut gon (bo phan trong ngoac neu co)
        display_color = color_name.split(' (')[0]
        
        if is_skin_tone(rgb):
            return f"👤 {display_color}"
        return f"👗 {display_color}"

    res_list = [{
        "name": get_display_name(final_color, is_human),
        "hex": COLOR_HEX[final_color],
        "confidence": max(1, final_confidence)
    }]
    for index, secondary_color in enumerate(secondary_colors):
        secondary_pixel_share = counts.get(secondary_color, 0) / max(1, len(pixels))
        secondary_vote_share = vote_counts.get(secondary_color, 0) / max(1, len(votes))
        confidence_weight = 0.55 if index == 0 else 0.45
        pixel_weight = 0.45 if index == 0 else 0.55
        confidence_cap = 95 if index == 0 else 88
        secondary_confidence = min(confidence_cap, int(round((secondary_vote_share * confidence_weight + secondary_pixel_share * pixel_weight) * 100)))
        
        res_list.append({
            "name": get_display_name(secondary_color, is_human),
            "hex": COLOR_HEX[secondary_color],
            "confidence": max(1, secondary_confidence)
        })
        
    return res_list

# --- GIAO DIEN ---

def copy_hex(index):
    if index >= len(current_results):
        return
    color_hex = current_results[index]["hex"]
    app.clipboard_clear()
    app.clipboard_append(color_hex)
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
            print(f"Analysis error: {e}")
            app.after(0, lambda: status_dot.configure(fg_color="red"))
            app.after(0, lambda: result_label1.configure(text="Lỗi phân tích!"))

    threading.Thread(target=run_analysis, daemon=True).start()

def finalize_render(image, results):
    global current_results
    current_results = results
    
    # Hien thi mau 1
    color1 = results[0]
    result_color_box1.configure(fg_color=color1["hex"])
    result_label1.configure(text=color1["name"])
    result_confidence1.configure(text=f"Tin cậy: {color1['confidence']}%")
    copy_btn1.configure(text=f"Copy {color1['hex']}")
    copy_btn1.pack(pady=(6, 0))
    
    # Hien thi mau 2
    if len(results) >= 2:
        color2 = results[1]
        result_color_box2.pack(before=result_label2, pady=2)
        result_color_box2.configure(fg_color=color2["hex"])
        result_label2.configure(text=color2["name"])
        result_confidence2.configure(text=f"Tin cậy: {color2['confidence']}%")
        copy_btn2.configure(text=f"Copy {color2['hex']}")
        copy_btn2.pack(pady=(6, 0))
        color1_frame.pack_configure(side="left", expand=True)
        color2_frame.pack(side="left", expand=True, fill="both", padx=5)
    else:
        result_color_box2.forget()
        result_label2.configure(text="")
        result_confidence2.configure(text="")
        copy_btn2.pack_forget()
        color1_frame.pack_configure(side="top", expand=True)
        color2_frame.pack_forget()

    # Hien thi mau 3
    if len(results) >= 3:
        color3 = results[2]
        result_color_box3.pack(before=result_label3, pady=2)
        result_color_box3.configure(fg_color=color3["hex"])
        result_label3.configure(text=color3["name"])
        result_confidence3.configure(text=f"Tin cậy: {color3['confidence']}%")
        copy_btn3.configure(text=f"Copy {color3['hex']}")
        copy_btn3.pack(pady=(6, 0))
        color1_frame.pack_configure(side="left", expand=True)
        color3_frame.pack(side="left", expand=True, fill="both", padx=5)
    else:
        result_color_box3.forget()
        result_label3.configure(text="")
        result_confidence3.configure(text="")
        copy_btn3.pack_forget()
        color3_frame.pack_forget()
        
    img_width, img_height = image.size
    ratio = min(150/img_width, 150/img_height)
    new_size = (int(img_width * ratio), int(img_height * ratio))
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
                signature = get_image_signature(image)
                if signature != last_clipboard_signature:
                    last_clipboard_signature = signature
                    render_analysis(image)
        except Exception:
            status_dot.configure(fg_color="red")
    app.after(1200, monitor_clipboard)

def toggle_pin():
    app.attributes('-topmost', pin_var.get())
    save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)

def change_opacity(value):
    global current_opacity
    current_opacity = float(value)
    app.attributes('-alpha', current_opacity)
    save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)
    if settings_opacity_val_label:
        settings_opacity_val_label.configure(text=f"{int(current_opacity * 100)}%")

# --- SETTINGS POPUP ---

settings_window_ref = None
settings_opacity_val_label = None

def open_settings():
    global settings_window_ref, settings_opacity_val_label
    # Neu da mo roi thi focus vao
    if settings_window_ref is not None and settings_window_ref.winfo_exists():
        settings_window_ref.lift()
        settings_window_ref.focus_force()
        return

    sw = ctk.CTkToplevel(app)
    sw.title("Cài đặt")
    sw.geometry("320x400")
    sw.resizable(False, False)
    sw.attributes('-topmost', True)
    sw.grab_set()  # Modal
    sw.focus_force()
    settings_window_ref = sw

    def on_close():
        global settings_window_ref
        settings_window_ref = None
        sw.destroy()
    sw.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkLabel(sw, text="⚙️ Cài đặt", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 10))

    # --- Do trong suot ---
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

    # --- Tu dong nhan anh tu Clipboard ---
    sep1 = ctk.CTkFrame(sw, height=1, fg_color="gray40")
    sep1.pack(fill="x", padx=20, pady=(4, 10))

    auto_cb_var = ctk.BooleanVar(value=auto_clipboard_enabled)

    def toggle_auto_clipboard():
        global auto_clipboard_enabled
        auto_clipboard_enabled = auto_cb_var.get()
        save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)

    auto_cb_switch = ctk.CTkSwitch(
        sw,
        text="📋 Tự động nhận ảnh từ Clipboard",
        variable=auto_cb_var,
        command=toggle_auto_clipboard,
        font=ctk.CTkFont(size=13)
    )
    auto_cb_switch.pack(anchor="w", padx=20, pady=(0, 10))

    def set_theme(choice):
        global current_theme
        current_theme = choice
        ctk.set_appearance_mode(choice)
        save_settings(pin_var.get(), current_opacity, current_theme, auto_clipboard_enabled)

    ctk.CTkLabel(sw, text="Giao diện (Theme):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
    theme_row = ctk.CTkFrame(sw, fg_color="transparent")
    theme_row.pack(fill="x", padx=15)
    
    # Su dung Segmented Button cho hien dai
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
    image_label.configure(image="", text="")
    result_color_box1.configure(fg_color="gray")
    result_color_box2.forget()
    result_color_box3.forget()
    result_label1.configure(text="")
    result_label2.configure(text="")
    result_label3.configure(text="")
    result_confidence1.configure(text="")
    result_confidence2.configure(text="")
    result_confidence3.configure(text="")
    copy_btn1.pack_forget()
    copy_btn2.pack_forget()
    copy_btn3.pack_forget()
    color1_frame.pack_configure(side="top", expand=True)
    color2_frame.pack_forget()
    color3_frame.pack_forget()
    
    # Xoa va an khung chon diem
    point_color_hex_label.configure(text="")
    point_color_name_label.configure(text="")
    point_color_box.configure(fg_color="gray20")
    point_copy_btn.pack_forget()
    point_color_frame.pack_forget() 
    
    status_dot.configure(fg_color="green")

# --- CHUC NANG CHON DIEM MAU (EYEDROPPER) ---

eyedropper_active   = False
eyedropper_overlay  = None   # Cua so toan man hinh - bat su kien chuot
eyedropper_loupe    = None   # Cua so loupe - chi hien thi zoom
eyedropper_canvas   = None
eyedropper_hex_label = None
eyedropper_screenshot = None

MAG_RADIUS     = 45   # Ban kinh loupe (px) - Nho gon hon
MAG_GRID_COUNT = 13   # So o luoi (le) - Tang do chinh xac

def start_eyedropper():
    """Bat dau che do chon diem mau"""
    global eyedropper_active
    if eyedropper_active:
        return
    eyedropper_active = True
    app.withdraw()
    # Dung after() thay vi sleep() de khong block UI
    app.after(180, _launch_eyedropper)

def _launch_eyedropper():
    """Duoc goi sau khi an cua so chinh"""
    global eyedropper_overlay, eyedropper_loupe, eyedropper_canvas
    global eyedropper_hex_label, eyedropper_screenshot

    try:
        eyedropper_screenshot = ImageGrab.grab()
    except Exception:
        cleanup_eyedropper()
        return

    scr_w = eyedropper_screenshot.width
    scr_h = eyedropper_screenshot.height
    loupe_size = MAG_RADIUS * 2 + 4

    # --- Overlay toan man hinh (gan vo hinh) bat tat ca click/motion ---
    overlay = tk.Toplevel()
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-alpha', 0.01)
    overlay.geometry(f"{scr_w}x{scr_h}+0+0")
    overlay.configure(cursor='crosshair', bg='black')
    eyedropper_overlay = overlay

    # --- Loupe: chi hien thi, khong bat su kien ---
    loupe = tk.Toplevel()
    loupe.overrideredirect(True)
    loupe.attributes('-topmost', True)
    loupe.attributes('-transparentcolor', 'magenta')
    loupe.configure(bg='magenta')
    loupe.geometry(f"{loupe_size}x{loupe_size + 28}+0+0")
    eyedropper_loupe = loupe

    canvas = tk.Canvas(loupe, width=loupe_size, height=loupe_size,
                       bg='magenta', highlightthickness=0, cursor='none')
    canvas.pack()
    eyedropper_canvas = canvas

    hex_lbl = tk.Label(loupe, text="#000000",
                       font=("Consolas", 10, "bold"),
                       fg="white", bg="#1a1a1a", padx=6, pady=2)
    hex_lbl.pack()
    eyedropper_hex_label = hex_lbl

    # Bind su kien tren overlay (toan man hinh)
    overlay.bind('<Motion>',   _on_motion)
    overlay.bind('<Button-1>', _on_click)
    overlay.bind('<Button-3>', _on_cancel)
    overlay.bind('<Escape>',   _on_cancel)
    overlay.focus_force()

    # Ve loupe lan dau
    mx = overlay.winfo_pointerx()
    my = overlay.winfo_pointery()
    _move_loupe(mx, my)
    _draw_loupe(mx, my)

def _on_motion(event):
    mx, my = event.x_root, event.y_root
    _move_loupe(mx, my)
    _draw_loupe(mx, my)

def _move_loupe(mx, my):
    if eyedropper_loupe is None or eyedropper_screenshot is None:
        return
    loupe_size = MAG_RADIUS * 2 + 4
    # Dat tam vong tron trung voi vi tri con tro
    lx = mx - loupe_size // 2
    ly = my - loupe_size // 2
    eyedropper_loupe.geometry(f"+{lx}+{ly}")

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

    mask = Image.new('L', (loupe_size, loupe_size), 0)
    ImageDraw.Draw(mask).ellipse([2, 2, loupe_size - 3, loupe_size - 3], fill=255)

    final = Image.new('RGB', (loupe_size, loupe_size), (255, 0, 255))
    final.paste(zoomed, (0, 0), mask)

    draw = ImageDraw.Draw(final)
    cell = loupe_size / MAG_GRID_COUNT
    grid_color = (60, 60, 60)
    
    # Ve luoi mo
    for i in range(MAG_GRID_COUNT + 1):
        p = int(i * cell)
        draw.line([(p, 0), (p, loupe_size)], fill=grid_color, width=1)
        draw.line([(0, p), (loupe_size, p)], fill=grid_color, width=1)

    # Crosshair trung tam (Box precision type)
    cx0 = int(half * cell);       cy0 = int(half * cell)
    cx1 = int((half+1) * cell);   cy1 = int((half+1) * cell)
    
    # Border cua o trung tam
    draw.rectangle([cx0-1, cy0-1, cx1+1, cy1+1], outline='#000000', width=1)
    draw.rectangle([cx0,   cy0,   cx1,   cy1  ], outline='#FFFFFF', width=1)

    final2 = Image.new('RGB', (loupe_size, loupe_size), (255, 0, 255))
    final2.paste(final, (0, 0), mask)
    
    # Vien ngoai loupe cao cap
    ImageDraw.Draw(final2).ellipse([1, 1, loupe_size-2, loupe_size-2], outline='#333333', width=2)
    ImageDraw.Draw(final2).ellipse([0, 0, loupe_size-1, loupe_size-1], outline='#888888', width=1)

    tk_img = ImageTk.PhotoImage(final2)
    eyedropper_canvas.delete('all')
    eyedropper_canvas.create_image(loupe_size // 2, loupe_size // 2, image=tk_img)
    eyedropper_canvas._ref = tk_img  # Giu tham chieu

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
    hex_color  = f"#{r:02X}{g:02X}{b:02X}"
    color_name = classify_pixel_hsv((r, g, b))[0]
    cleanup_eyedropper()
    render_point_color((r, g, b), hex_color, color_name)

def _on_cancel(event=None):
    cleanup_eyedropper()

def cleanup_eyedropper():
    global eyedropper_active, eyedropper_overlay, eyedropper_loupe
    global eyedropper_canvas, eyedropper_hex_label, eyedropper_screenshot
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

def render_point_color(rgb, hex_color, color_name):
    global picked_point_color
    picked_point_color = hex_color
    point_color_box.configure(fg_color=hex_color)
    point_color_hex_label.configure(text=hex_color)
    point_color_name_label.configure(text=color_name.upper())
    point_copy_btn.configure(text=f"Copy {hex_color}")
    point_copy_btn.pack(pady=(4, 0))
    point_color_frame.pack(pady=(2, 0), fill="x", padx=15, before=status_dot) # Hien thi khung khi co mau
    status_dot.configure(fg_color="#6366f1")

def copy_point_hex():
    if picked_point_color:
        app.clipboard_clear()
        app.clipboard_append(picked_point_color)
        app.update()
        status_dot.configure(fg_color="dodgerblue")

picked_point_color = None

app_settings = load_settings()
current_opacity = app_settings.get("opacity", 1.0)
current_theme = app_settings.get("theme", "System")
auto_clipboard_enabled = app_settings.get("auto_clipboard", True)

ctk.set_appearance_mode(current_theme)
ctk.set_default_color_theme("blue") # Blue is a good base, but we will customize buttons

app = ctk.CTk()
app.title("Color Picker v2.1")
app.geometry("360x485")
app.attributes('-alpha', current_opacity)
app.attributes('-topmost', app_settings.get("topmost", False))
app.minsize(340, 460)

top_frame = ctk.CTkFrame(app, fg_color="transparent")
top_frame.pack(fill="x", padx=15, pady=(10, 5))

pin_var = ctk.BooleanVar(value=app_settings.get("topmost", False))
pin_switch = ctk.CTkSwitch(top_frame, text="Ghim", variable=pin_var, command=toggle_pin)
pin_switch.pack(side="left")

eyedropper_btn = ctk.CTkButton(
    top_frame, text="🎯 Pick", width=100, height=32,
    fg_color="#6366f1", hover_color="#4f46e5", # Indigo premium
    font=ctk.CTkFont(size=13, weight="bold"),
    command=start_eyedropper
)
eyedropper_btn.pack(side="left", padx=8)

# Nut Settings icon (ben phai, truoc Reset)
settings_btn = ctk.CTkButton(
    top_frame, text="⚙️", width=36, height=32,
    fg_color="#334155", hover_color="#475569", # Slate premium
    font=ctk.CTkFont(size=14),
    command=open_settings
)
settings_btn.pack(side="right", padx=(4, 0))

reset_btn = ctk.CTkButton(top_frame, text="Reset", width=55, height=28, fg_color="#c0392b", hover_color="#e74c3c", command=reset_app)
reset_btn.pack(side="right", padx=(0, 4))

# (Opacity slider da chuyen vao Settings popup)

image_frame = ctk.CTkFrame(app, width=120, height=120, fg_color="gray20", corner_radius=12)
image_frame.pack(pady=(5, 5))
image_frame.pack_propagate(False)
image_label = ctk.CTkLabel(image_frame, text="", text_color="gray60", font=ctk.CTkFont(size=11))
image_label.pack(expand=True, fill="both")

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
copy_btn1 = ctk.CTkButton(color1_frame, text="Sao chép HEX", width=100, height=26, font=ctk.CTkFont(size=11), command=lambda: copy_hex(0))

color2_frame = ctk.CTkFrame(result_container, fg_color="transparent")
result_color_box2 = ctk.CTkFrame(color2_frame, width=28, height=28, corner_radius=6, fg_color="transparent")
result_color_box2.pack(pady=1)
result_label2 = ctk.CTkLabel(color2_frame, text="", font=ctk.CTkFont(size=15, weight="bold"))
result_label2.pack()
result_confidence2 = ctk.CTkLabel(color2_frame, text="", text_color="gray70", font=ctk.CTkFont(size=11))
result_confidence2.pack()
copy_btn2 = ctk.CTkButton(color2_frame, text="Sao chép HEX", width=100, height=26, font=ctk.CTkFont(size=11), command=lambda: copy_hex(1))

color3_frame = ctk.CTkFrame(result_container, fg_color="transparent")
result_color_box3 = ctk.CTkFrame(color3_frame, width=28, height=28, corner_radius=6, fg_color="transparent")
result_color_box3.pack(pady=1)
result_label3 = ctk.CTkLabel(color3_frame, text="", font=ctk.CTkFont(size=15, weight="bold"))
result_label3.pack()
result_confidence3 = ctk.CTkLabel(color3_frame, text="", text_color="gray70", font=ctk.CTkFont(size=11))
result_confidence3.pack()
copy_btn3 = ctk.CTkButton(color3_frame, text="Sao chép HEX", width=100, height=26, font=ctk.CTkFont(size=11), command=lambda: copy_hex(2))

# --- KHUNG KET QUA CHON DIEM MAU ---
point_color_frame = ctk.CTkFrame(app, fg_color="transparent")
# initial: point_color_frame.pack_forget() 

point_color_title = ctk.CTkLabel(
    point_color_frame, text="🎯 Color Picked:",
    font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70"
)
point_color_title.pack(anchor="w", padx=5)

point_color_inner = ctk.CTkFrame(point_color_frame, fg_color="transparent")
point_color_inner.pack(fill="x", padx=5, pady=0)

point_color_box = ctk.CTkFrame(point_color_inner, width=28, height=28, corner_radius=6, fg_color="gray20")
point_color_box.pack(side="left", padx=(0, 6))

point_color_hex_label = ctk.CTkLabel(
    point_color_inner, text="",
    font=ctk.CTkFont(family="Consolas", size=14, weight="bold")
)
point_color_hex_label.pack(side="left", padx=(0, 6))

point_color_name_label = ctk.CTkLabel(
    point_color_inner, text="",
    font=ctk.CTkFont(size=12), text_color="gray70"
)
point_color_name_label.pack(side="left")

point_copy_btn = ctk.CTkButton(
    point_color_frame, text="Sao chép mã màu", width=100, height=26,
    fg_color="#6366f1", hover_color="#4f46e5", font=ctk.CTkFont(size=11),
    command=copy_point_hex
)

status_dot = ctk.CTkFrame(app, width=10, height=10, corner_radius=5, fg_color="green")
status_dot.pack(pady=10, side="bottom")

app.bind("<Control-v>", analyze_clipboard_image)
app.bind("<Control-V>", analyze_clipboard_image)
app.after(1200, monitor_clipboard)

if __name__ == "__main__":
    if keyboard:
        try:
            # Dung Alt+X va Alt+S lam phim tat chinh
            keyboard.add_hotkey('alt+x', lambda: app.after(0, start_eyedropper), suppress=True)
            keyboard.add_hotkey('alt+s', lambda: app.after(0, start_eyedropper), suppress=True)
        except Exception:
            pass
    single_instance_check()
    app.mainloop()
