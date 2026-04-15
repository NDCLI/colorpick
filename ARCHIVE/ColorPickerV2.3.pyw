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
import ctypes.wintypes
import atexit
# keyboard library removed in favor of native Win32 RegisterHotKey for stability

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

# --- DIEU CHINH TOC DO CHUOT ---
SPI_GETMOUSESPEED = 112
SPI_SETMOUSESPEED = 113
original_mouse_speed = None
precision_mouse_speed = 3  # Toc do cham de ve chinh xac

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
    except:
        pass

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
    "Snow": "#FFFAFA",
    "GhostWhite": "#F8F8FF",
    "WhiteSmoke": "#F5F5F5",
    "Gainsboro": "#DCDCDC",
    "FloralWhite": "#FFFAF0",
    "OldLace": "#FDF5E6",
    "Linen": "#FAF0E6",
    "AntiqueWhite": "#FAEBD7",
    "PapayaWhip": "#FFEFD5",
    "BlanchedAlmond": "#FFEBCD",
    "Bisque": "#FFE4C4",
    "PeachPuff": "#FFDAB9",
    "NavajoWhite": "#FFDEAD",
    "Moccasin": "#FFE4B5",
    "Cornsilk": "#FFF8DC",
    "Ivory": "#FFFFF0",
    "LemonChiffon": "#FFFACD",
    "Seashell": "#FFF5EE",
    "Honeydew": "#F0FFF0",
    "MintCream": "#F5FFFA",
    "Azure": "#F0FFFF",
    "AliceBlue": "#F0F8FF",
    "Lavender": "#E6E6FA",
    "LavenderBlush": "#FFF0F5",
    "MistyRose": "#FFE4E1",
    "White": "#FFFFFF",
    "Black": "#000000",
    "DarkSlateGray": "#2F4F4F",
    "DimGray": "#696969",
    "SlateGray": "#708090",
    "LightSlateGray": "#778899",
    "Gray": "#BEBEBE",
    "X11Gray": "#BEBEBE",
    "WebGray": "#808080",
    "LightGray": "#D3D3D3",
    "MidnightBlue": "#191970",
    "Navy": "#000080",
    "NavyBlue": "#000080",
    "CornflowerBlue": "#6495ED",
    "DarkSlateBlue": "#483D8B",
    "SlateBlue": "#6A5ACD",
    "MediumSlateBlue": "#7B68EE",
    "LightSlateBlue": "#8470FF",
    "MediumBlue": "#0000CD",
    "RoyalBlue": "#4169E1",
    "Blue": "#0000FF",
    "DodgerBlue": "#1E90FF",
    "DeepSkyBlue": "#00BFFF",
    "SkyBlue": "#87CEEB",
    "LightSkyBlue": "#87CEFA",
    "SteelBlue": "#4682B4",
    "LightSteelBlue": "#B0C4DE",
    "LightBlue": "#ADD8E6",
    "PowderBlue": "#B0E0E6",
    "PaleTurquoise": "#AFEEEE",
    "DarkTurquoise": "#00CED1",
    "MediumTurquoise": "#48D1CC",
    "Turquoise": "#40E0D0",
    "Cyan": "#00FFFF",
    "Aqua": "#00FFFF",
    "LightCyan": "#E0FFFF",
    "CadetBlue": "#5F9EA0",
    "MediumAquamarine": "#66CDAA",
    "Aquamarine": "#7FFFD4",
    "DarkGreen": "#006400",
    "DarkOliveGreen": "#556B2F",
    "DarkSeaGreen": "#8FBC8F",
    "SeaGreen": "#2E8B57",
    "MediumSeaGreen": "#3CB371",
    "LightSeaGreen": "#20B2AA",
    "PaleGreen": "#98FB98",
    "SpringGreen": "#00FF7F",
    "LawnGreen": "#7CFC00",
    "Green": "#00FF00",
    "Lime": "#00FF00",
    "X11Green": "#00FF00",
    "WebGreen": "#008000",
    "Chartreuse": "#7FFF00",
    "MediumSpringGreen": "#00FA9A",
    "GreenYellow": "#ADFF2F",
    "LimeGreen": "#32CD32",
    "YellowGreen": "#9ACD32",
    "ForestGreen": "#228B22",
    "OliveDrab": "#6B8E23",
    "DarkKhaki": "#BDB76B",
    "Khaki": "#F0E68C",
    "PaleGoldenrod": "#EEE8AA",
    "LightGoldenrodYellow": "#FAFAD2",
    "LightYellow": "#FFFFE0",
    "Yellow": "#FFFF00",
    "Gold": "#FFD700",
    "LightGoldenrod": "#EEDD82",
    "Goldenrod": "#DAA520",
    "DarkGoldenrod": "#B8860B",
    "RosyBrown": "#BC8F8F",
    "IndianRed": "#CD5C5C",
    "SaddleBrown": "#8B4513",
    "Sienna": "#A0522D",
    "Peru": "#CD853F",
    "Burlywood": "#DEB887",
    "Beige": "#F5F5DC",
    "Wheat": "#F5DEB3",
    "SandyBrown": "#F4A460",
    "Tan": "#D2B48C",
    "Chocolate": "#D2691E",
    "Firebrick": "#B22222",
    "Brown": "#A52A2A",
    "DarkSalmon": "#E9967A",
    "Salmon": "#FA8072",
    "LightSalmon": "#FFA07A",
    "Orange": "#FFA500",
    "DarkOrange": "#FF8C00",
    "Coral": "#FF7F50",
    "LightCoral": "#F08080",
    "Tomato": "#FF6347",
    "OrangeRed": "#FF4500",
    "Red": "#FF0000",
    "HotPink": "#FF69B4",
    "DeepPink": "#FF1493",
    "Pink": "#FFC0CB",
    "LightPink": "#FFB6C1",
    "PaleVioletRed": "#DB7093",
    "Maroon": "#B03060",
    "X11Maroon": "#B03060",
    "WebMaroon": "#800000",
    "MediumVioletRed": "#C71585",
    "VioletRed": "#D02090",
    "Magenta": "#FF00FF",
    "Fuchsia": "#FF00FF",
    "Violet": "#EE82EE",
    "Plum": "#DDA0DD",
    "Orchid": "#DA70D6",
    "MediumOrchid": "#BA55D3",
    "DarkOrchid": "#9932CC",
    "DarkViolet": "#9400D3",
    "BlueViolet": "#8A2BE2",
    "Purple": "#A020F0",
    "X11Purple": "#A020F0",
    "WebPurple": "#800080",
    "MediumPurple": "#9370DB",
    "Thistle": "#D8BFD8",
    "Snow1": "#FFFAFA",
    "Snow2": "#EEE9E9",
    "Snow3": "#CDC9C9",
    "Snow4": "#8B8989",
    "Seashell1": "#FFF5EE",
    "Seashell2": "#EEE5DE",
    "Seashell3": "#CDC5BF",
    "Seashell4": "#8B8682",
    "AntiqueWhite1": "#FFEFDB",
    "AntiqueWhite2": "#EEDFCC",
    "AntiqueWhite3": "#CDC0B0",
    "AntiqueWhite4": "#8B8378",
    "Bisque1": "#FFE4C4",
    "Bisque2": "#EED5B7",
    "Bisque3": "#CDB79E",
    "Bisque4": "#8B7D6B",
    "PeachPuff1": "#FFDAB9",
    "PeachPuff2": "#EECBAD",
    "PeachPuff3": "#CDAF95",
    "PeachPuff4": "#8B7765",
    "NavajoWhite1": "#FFDEAD",
    "NavajoWhite2": "#EECFA1",
    "NavajoWhite3": "#CDB38B",
    "NavajoWhite4": "#8B795E",
    "LemonChiffon1": "#FFFACD",
    "LemonChiffon2": "#EEE9BF",
    "LemonChiffon3": "#CDC9A5",
    "LemonChiffon4": "#8B8970",
    "Cornsilk1": "#FFF8DC",
    "Cornsilk2": "#EEE8CD",
    "Cornsilk3": "#CDC8B1",
    "Cornsilk4": "#8B8878",
    "Ivory1": "#FFFFF0",
    "Ivory2": "#EEEEE0",
    "Ivory3": "#CDCDC1",
    "Ivory4": "#8B8B83",
    "Honeydew1": "#F0FFF0",
    "Honeydew2": "#E0EEE0",
    "Honeydew3": "#C1CDC1",
    "Honeydew4": "#838B83",
    "LavenderBlush1": "#FFF0F5",
    "LavenderBlush2": "#EEE0E5",
    "LavenderBlush3": "#CDC1C5",
    "LavenderBlush4": "#8B8386",
    "MistyRose1": "#FFE4E1",
    "MistyRose2": "#EED5D2",
    "MistyRose3": "#CDB7B5",
    "MistyRose4": "#8B7D7B",
    "Azure1": "#F0FFFF",
    "Azure2": "#E0EEEE",
    "Azure3": "#C1CDCD",
    "Azure4": "#838B8B",
    "SlateBlue1": "#836FFF",
    "SlateBlue2": "#7A67EE",
    "SlateBlue3": "#6959CD",
    "SlateBlue4": "#473C8B",
    "RoyalBlue1": "#4876FF",
    "RoyalBlue2": "#436EEE",
    "RoyalBlue3": "#3A5FCD",
    "RoyalBlue4": "#27408B",
    "Blue1": "#0000FF",
    "Blue2": "#0000EE",
    "Blue3": "#0000CD",
    "Blue4": "#00008B",
    "DodgerBlue1": "#1E90FF",
    "DodgerBlue2": "#1C86EE",
    "DodgerBlue3": "#1874CD",
    "DodgerBlue4": "#104E8B",
    "SteelBlue1": "#63B8FF",
    "SteelBlue2": "#5CACEE",
    "SteelBlue3": "#4F94CD",
    "SteelBlue4": "#36648B",
    "DeepSkyBlue1": "#00BFFF",
    "DeepSkyBlue2": "#00B2EE",
    "DeepSkyBlue3": "#009ACD",
    "DeepSkyBlue4": "#00688B",
    "SkyBlue1": "#87CEFF",
    "SkyBlue2": "#7EC0EE",
    "SkyBlue3": "#6CA6CD",
    "SkyBlue4": "#4A708B",
    "LightSkyBlue1": "#B0E2FF",
    "LightSkyBlue2": "#A4D3EE",
    "LightSkyBlue3": "#8DB6CD",
    "LightSkyBlue4": "#607B8B",
    "SlateGray1": "#C6E2FF",
    "SlateGray2": "#B9D3EE",
    "SlateGray3": "#9FB6CD",
    "SlateGray4": "#6C7B8B",
    "LightSteelBlue1": "#CAE1FF",
    "LightSteelBlue2": "#BCD2EE",
    "LightSteelBlue3": "#A2B5CD",
    "LightSteelBlue4": "#6E7B8B",
    "LightBlue1": "#BFEFFF",
    "LightBlue2": "#B2DFEE",
    "LightBlue3": "#9AC0CD",
    "LightBlue4": "#68838B",
    "LightCyan1": "#E0FFFF",
    "LightCyan2": "#D1EEEE",
    "LightCyan3": "#B4CDCD",
    "LightCyan4": "#7A8B8B",
    "PaleTurquoise1": "#BBFFFF",
    "PaleTurquoise2": "#AEEEEE",
    "PaleTurquoise3": "#96CDCD",
    "PaleTurquoise4": "#668B8B",
    "CadetBlue1": "#98F5FF",
    "CadetBlue2": "#8EE5EE",
    "CadetBlue3": "#7AC5CD",
    "CadetBlue4": "#53868B",
    "Turquoise1": "#00F5FF",
    "Turquoise2": "#00E5EE",
    "Turquoise3": "#00C5CD",
    "Turquoise4": "#00868B",
    "Cyan1": "#00FFFF",
    "Cyan2": "#00EEEE",
    "Cyan3": "#00CDCD",
    "Cyan4": "#008B8B",
    "DarkSlateGray1": "#97FFFF",
    "DarkSlateGray2": "#8DEEEE",
    "DarkSlateGray3": "#79CDCD",
    "DarkSlateGray4": "#528B8B",
    "Aquamarine1": "#7FFFD4",
    "Aquamarine2": "#76EEC6",
    "Aquamarine3": "#66CDAA",
    "Aquamarine4": "#458B74",
    "DarkSeaGreen1": "#C1FFC1",
    "DarkSeaGreen2": "#B4EEB4",
    "DarkSeaGreen3": "#9BCD9B",
    "DarkSeaGreen4": "#698B69",
    "SeaGreen1": "#54FF9F",
    "SeaGreen2": "#4EEE94",
    "SeaGreen3": "#43CD80",
    "SeaGreen4": "#2E8B57",
    "PaleGreen1": "#9AFF9A",
    "PaleGreen2": "#90EE90",
    "PaleGreen3": "#7CCD7C",
    "PaleGreen4": "#548B54",
    "SpringGreen1": "#00FF7F",
    "SpringGreen2": "#00EE76",
    "SpringGreen3": "#00CD66",
    "SpringGreen4": "#008B45",
    "Green1": "#00FF00",
    "Green2": "#00EE00",
    "Green3": "#00CD00",
    "Green4": "#008B00",
    "Chartreuse1": "#7FFF00",
    "Chartreuse2": "#76EE00",
    "Chartreuse3": "#66CD00",
    "Chartreuse4": "#458B00",
    "OliveDrab1": "#C0FF3E",
    "OliveDrab2": "#B3EE3A",
    "OliveDrab3": "#9ACD32",
    "OliveDrab4": "#698B22",
    "DarkOliveGreen1": "#CAFF70",
    "DarkOliveGreen2": "#BCEE68",
    "DarkOliveGreen3": "#A2CD5A",
    "DarkOliveGreen4": "#6E8B3D",
    "Khaki1": "#FFF68F",
    "Khaki2": "#EEE685",
    "Khaki3": "#CDC673",
    "Khaki4": "#8B864E",
    "LightGoldenrod1": "#FFEC8B",
    "LightGoldenrod2": "#EEDC82",
    "LightGoldenrod3": "#CDBE70",
    "LightGoldenrod4": "#8B814C",
    "LightYellow1": "#FFFFE0",
    "LightYellow2": "#EEEED1",
    "LightYellow3": "#CDCDB4",
    "LightYellow4": "#8B8B7A",
    "Yellow1": "#FFFF00",
    "Yellow2": "#EEEE00",
    "Yellow3": "#CDCD00",
    "Yellow4": "#8B8B00",
    "Gold1": "#FFD700",
    "Gold2": "#EEC900",
    "Gold3": "#CDAD00",
    "Gold4": "#8B7500",
    "Goldenrod1": "#FFC125",
    "Goldenrod2": "#EEB422",
    "Goldenrod3": "#CD9B1D",
    "Goldenrod4": "#8B6914",
    "DarkGoldenrod1": "#FFB90F",
    "DarkGoldenrod2": "#EEAD0E",
    "DarkGoldenrod3": "#CD950C",
    "DarkGoldenrod4": "#8B6508",
    "RosyBrown1": "#FFC1C1",
    "RosyBrown2": "#EEB4B4",
    "RosyBrown3": "#CD9B9B",
    "RosyBrown4": "#8B6969",
    "IndianRed1": "#FF6A6A",
    "IndianRed2": "#EE6363",
    "IndianRed3": "#CD5555",
    "IndianRed4": "#8B3A3A",
    "Sienna1": "#FF8247",
    "Sienna2": "#EE7942",
    "Sienna3": "#CD6839",
    "Sienna4": "#8B4726",
    "Burlywood1": "#FFD39B",
    "Burlywood2": "#EEC591",
    "Burlywood3": "#CDAA7D",
    "Burlywood4": "#8B7355",
    "Wheat1": "#FFE7BA",
    "Wheat2": "#EED8AE",
    "Wheat3": "#CDBA96",
    "Wheat4": "#8B7E66",
    "Tan1": "#FFA54F",
    "Tan2": "#EE9A49",
    "Tan3": "#CD853F",
    "Tan4": "#8B5A2B",
    "Chocolate1": "#FF7F24",
    "Chocolate2": "#EE7621",
    "Chocolate3": "#CD661D",
    "Chocolate4": "#8B4513",
    "Firebrick1": "#FF3030",
    "Firebrick2": "#EE2C2C",
    "Firebrick3": "#CD2626",
    "Firebrick4": "#8B1A1A",
    "Brown1": "#FF4040",
    "Brown2": "#EE3B3B",
    "Brown3": "#CD3333",
    "Brown4": "#8B2323",
    "Salmon1": "#FF8C69",
    "Salmon2": "#EE8262",
    "Salmon3": "#CD7054",
    "Salmon4": "#8B4C39",
    "LightSalmon1": "#FFA07A",
    "LightSalmon2": "#EE9572",
    "LightSalmon3": "#CD8162",
    "LightSalmon4": "#8B5742",
    "Orange1": "#FFA500",
    "Orange2": "#EE9A00",
    "Orange3": "#CD8500",
    "Orange4": "#8B5A00",
    "DarkOrange1": "#FF7F00",
    "DarkOrange2": "#EE7600",
    "DarkOrange3": "#CD6600",
    "DarkOrange4": "#8B4500",
    "Coral1": "#FF7256",
    "Coral2": "#EE6A50",
    "Coral3": "#CD5B45",
    "Coral4": "#8B3E2F",
    "Tomato1": "#FF6347",
    "Tomato2": "#EE5C42",
    "Tomato3": "#CD4F39",
    "Tomato4": "#8B3626",
    "OrangeRed1": "#FF4500",
    "OrangeRed2": "#EE4000",
    "OrangeRed3": "#CD3700",
    "OrangeRed4": "#8B2500",
    "Red1": "#FF0000",
    "Red2": "#EE0000",
    "Red3": "#CD0000",
    "Red4": "#8B0000",
    "DeepPink1": "#FF1493",
    "DeepPink2": "#EE1289",
    "DeepPink3": "#CD1076",
    "DeepPink4": "#8B0A50",
    "HotPink1": "#FF6EB4",
    "HotPink2": "#EE6AA7",
    "HotPink3": "#CD6090",
    "HotPink4": "#8B3A62",
    "Pink1": "#FFB5C5",
    "Pink2": "#EEA9B8",
    "Pink3": "#CD919E",
    "Pink4": "#8B636C",
    "LightPink1": "#FFAEB9",
    "LightPink2": "#EEA2AD",
    "LightPink3": "#CD8C95",
    "LightPink4": "#8B5F65",
    "PaleVioletRed1": "#FF82AB",
    "PaleVioletRed2": "#EE799F",
    "PaleVioletRed3": "#CD6889",
    "PaleVioletRed4": "#8B475D",
    "Maroon1": "#FF34B3",
    "Maroon2": "#EE30A7",
    "Maroon3": "#CD2990",
    "Maroon4": "#8B1C62",
    "VioletRed1": "#FF3E96",
    "VioletRed2": "#EE3A8C",
    "VioletRed3": "#CD3278",
    "VioletRed4": "#8B2252",
    "Magenta1": "#FF00FF",
    "Magenta2": "#EE00EE",
    "Magenta3": "#CD00CD",
    "Magenta4": "#8B008B",
    "Orchid1": "#FF83FA",
    "Orchid2": "#EE7AE9",
    "Orchid3": "#CD69C9",
    "Orchid4": "#8B4789",
    "Plum1": "#FFBBFF",
    "Plum2": "#EEAEEE",
    "Plum3": "#CD96CD",
    "Plum4": "#8B668B",
    "MediumOrchid1": "#E066FF",
    "MediumOrchid2": "#D15FEE",
    "MediumOrchid3": "#B452CD",
    "MediumOrchid4": "#7A378B",
    "DarkOrchid1": "#BF3EFF",
    "DarkOrchid2": "#B23AEE",
    "DarkOrchid3": "#9A32CD",
    "DarkOrchid4": "#68228B",
    "Purple1": "#9B30FF",
    "Purple2": "#912CEE",
    "Purple3": "#7D26CD",
    "Purple4": "#551A8B",
    "MediumPurple1": "#AB82FF",
    "MediumPurple2": "#9F79EE",
    "MediumPurple3": "#8968CD",
    "MediumPurple4": "#5D478B",
    "Thistle1": "#FFE1FF",
    "Thistle2": "#EED2EE",
    "Thistle3": "#CDB5CD",
    "Thistle4": "#8B7B8B",
    "Gray0": "#000000",
    "Gray1": "#030303",
    "Gray2": "#050505",
    "Gray3": "#080808",
    "Gray4": "#0A0A0A",
    "Gray5": "#0D0D0D",
    "Gray6": "#0F0F0F",
    "Gray7": "#121212",
    "Gray8": "#141414",
    "Gray9": "#171717",
    "Gray10": "#1A1A1A",
    "Gray11": "#1C1C1C",
    "Gray12": "#1F1F1F",
    "Gray13": "#212121",
    "Gray14": "#242424",
    "Gray15": "#262626",
    "Gray16": "#292929",
    "Gray17": "#2B2B2B",
    "Gray18": "#2E2E2E",
    "Gray19": "#303030",
    "Gray20": "#333333",
    "Gray21": "#363636",
    "Gray22": "#383838",
    "Gray23": "#3B3B3B",
    "Gray24": "#3D3D3D",
    "Gray25": "#404040",
    "Gray26": "#424242",
    "Gray27": "#454545",
    "Gray28": "#474747",
    "Gray29": "#4A4A4A",
    "Gray30": "#4D4D4D",
    "Gray31": "#4F4F4F",
    "Gray32": "#525252",
    "Gray33": "#545454",
    "Gray34": "#575757",
    "Gray35": "#595959",
    "Gray36": "#5C5C5C",
    "Gray37": "#5E5E5E",
    "Gray38": "#616161",
    "Gray39": "#636363",
    "Gray40": "#666666",
    "Gray41": "#696969",
    "Gray42": "#6B6B6B",
    "Gray43": "#6E6E6E",
    "Gray44": "#707070",
    "Gray45": "#737373",
    "Gray46": "#757575",
    "Gray47": "#787878",
    "Gray48": "#7A7A7A",
    "Gray49": "#7D7D7D",
    "Gray50": "#7F7F7F",
    "Gray51": "#828282",
    "Gray52": "#858585",
    "Gray53": "#878787",
    "Gray54": "#8A8A8A",
    "Gray55": "#8C8C8C",
    "Gray56": "#8F8F8F",
    "Gray57": "#919191",
    "Gray58": "#949494",
    "Gray59": "#969696",
    "Gray60": "#999999",
    "Gray61": "#9C9C9C",
    "Gray62": "#9E9E9E",
    "Gray63": "#A1A1A1",
    "Gray64": "#A3A3A3",
    "Gray65": "#A6A6A6",
    "Gray66": "#A8A8A8",
    "Gray67": "#ABABAB",
    "Gray68": "#ADADAD",
    "Gray69": "#B0B0B0",
    "Gray70": "#B3B3B3",
    "Gray71": "#B5B5B5",
    "Gray72": "#B8B8B8",
    "Gray73": "#BABABA",
    "Gray74": "#BDBDBD",
    "Gray75": "#BFBFBF",
    "Gray76": "#C2C2C2",
    "Gray77": "#C4C4C4",
    "Gray78": "#C7C7C7",
    "Gray79": "#C9C9C9",
    "Gray80": "#CCCCCC",
    "Gray81": "#CFCFCF",
    "Gray82": "#D1D1D1",
    "Gray83": "#D4D4D4",
    "Gray84": "#D6D6D6",
    "Gray85": "#D9D9D9",
    "Gray86": "#DBDBDB",
    "Gray87": "#DEDEDE",
    "Gray88": "#E0E0E0",
    "Gray89": "#E3E3E3",
    "Gray90": "#E5E5E5",
    "Gray91": "#E8E8E8",
    "Gray92": "#EBEBEB",
    "Gray93": "#EDEDED",
    "Gray94": "#F0F0F0",
    "Gray95": "#F2F2F2",
    "Gray96": "#F5F5F5",
    "Gray97": "#F7F7F7",
    "Gray98": "#FAFAFA",
    "Gray99": "#FCFCFC",
    "Gray100": "#FFFFFF",
    "DarkGray": "#A9A9A9",
    "DarkBlue": "#00008B",
    "DarkCyan": "#008B8B",
    "DarkMagenta": "#8B008B",
    "DarkRed": "#8B0000",
    "LightGreen": "#90EE90",
    "Crimson": "#DC143C",
    "Indigo": "#4B0082",
    "Olive": "#808000",
    "RebeccaPurple": "#663399",
    "Silver": "#C0C0C0",
    "Teal": "#008080",
}

LAB_REFERENCE = {
    "Snow": (98.64, 1.66, 0.58),
    "GhostWhite": (97.76, 1.25, -3.36),
    "WhiteSmoke": (96.54, 0.01, -0.01),
    "Gainsboro": (87.76, 0.0, -0.01),
    "FloralWhite": (98.4, -0.03, 5.37),
    "OldLace": (96.78, 0.18, 8.16),
    "Linen": (95.31, 1.68, 6.01),
    "AntiqueWhite": (93.73, 1.84, 11.52),
    "PapayaWhip": (95.08, 1.27, 14.52),
    "BlanchedAlmond": (93.92, 2.13, 17.02),
    "Bisque": (92.01, 4.43, 19.0),
    "PeachPuff": (89.35, 8.09, 21.01),
    "NavajoWhite": (90.1, 4.51, 28.26),
    "Moccasin": (91.72, 2.44, 26.35),
    "Cornsilk": (97.46, -2.21, 14.28),
    "Ivory": (99.64, -2.55, 7.15),
    "LemonChiffon": (97.65, -5.42, 22.23),
    "Seashell": (97.12, 2.17, 4.54),
    "Honeydew": (98.57, -7.56, 5.47),
    "MintCream": (99.16, -4.16, 1.24),
    "Azure": (98.93, -4.88, -1.7),
    "AliceBlue": (97.18, -1.34, -4.27),
    "Lavender": (91.83, 3.71, -9.67),
    "LavenderBlush": (96.07, 5.89, -0.6),
    "MistyRose": (92.66, 8.75, 4.83),
    "White": (100.0, 0.01, -0.01),
    "Black": (0.0, 0.0, 0.0),
    "DarkSlateGray": (31.26, -11.72, -3.73),
    "DimGray": (44.41, 0.0, -0.01),
    "SlateGray": (52.84, -2.14, -10.58),
    "LightSlateGray": (55.92, -2.24, -11.11),
    "Gray": (76.98, 0.0, -0.01),
    "X11Gray": (76.98, 0.0, -0.01),
    "WebGray": (53.59, 0.0, -0.01),
    "LightGray": (84.56, 0.0, -0.01),
    "MidnightBlue": (15.86, 31.72, -49.58),
    "Navy": (12.98, 47.51, -64.7),
    "NavyBlue": (12.98, 47.51, -64.7),
    "CornflowerBlue": (61.93, 9.34, -49.31),
    "DarkSlateBlue": (30.83, 26.06, -42.09),
    "SlateBlue": (45.34, 36.05, -57.78),
    "MediumSlateBlue": (52.16, 41.08, -65.41),
    "LightSlateBlue": (55.8, 43.21, -68.93),
    "MediumBlue": (24.98, 67.18, -91.5),
    "RoyalBlue": (47.83, 26.27, -65.27),
    "Blue": (32.3, 79.2, -107.86),
    "DodgerBlue": (59.38, 9.97, -63.39),
    "DeepSkyBlue": (72.55, -17.65, -42.55),
    "SkyBlue": (79.21, -14.83, -21.28),
    "LightSkyBlue": (79.73, -10.82, -28.51),
    "SteelBlue": (52.47, -4.07, -32.2),
    "LightSteelBlue": (78.45, -1.28, -15.22),
    "LightBlue": (83.81, -10.89, -11.49),
    "PowderBlue": (86.13, -14.09, -8.02),
    "PaleTurquoise": (90.06, -19.63, -6.41),
    "DarkTurquoise": (75.29, -40.04, -13.52),
    "MediumTurquoise": (76.88, -37.35, -8.36),
    "Turquoise": (81.27, -44.08, -4.03),
    "Cyan": (91.12, -48.08, -14.14),
    "Aqua": (91.12, -48.08, -14.14),
    "LightCyan": (97.87, -9.94, -3.38),
    "CadetBlue": (61.15, -19.68, -7.43),
    "MediumAquamarine": (75.69, -38.33, 8.3),
    "Aquamarine": (92.04, -45.52, 9.71),
    "DarkGreen": (36.2, -43.37, 41.86),
    "DarkOliveGreen": (42.23, -18.83, 30.6),
    "DarkSeaGreen": (72.09, -23.82, 18.03),
    "SeaGreen": (51.54, -39.71, 20.05),
    "MediumSeaGreen": (65.27, -48.22, 24.29),
    "LightSeaGreen": (65.79, -37.51, -6.34),
    "PaleGreen": (90.75, -48.3, 38.52),
    "SpringGreen": (88.47, -76.9, 47.03),
    "LawnGreen": (88.88, -67.86, 84.95),
    "Green": (87.74, -86.18, 83.18),
    "Lime": (87.74, -86.18, 83.18),
    "X11Green": (87.74, -86.18, 83.18),
    "WebGreen": (46.23, -51.7, 49.9),
    "Chartreuse": (89.87, -68.07, 85.78),
    "MediumSpringGreen": (87.34, -70.68, 32.46),
    "GreenYellow": (91.96, -52.48, 81.87),
    "LimeGreen": (72.61, -67.13, 61.44),
    "YellowGreen": (76.54, -37.99, 66.59),
    "ForestGreen": (50.59, -49.59, 45.02),
    "OliveDrab": (54.65, -28.22, 49.69),
    "DarkKhaki": (73.38, -8.79, 39.29),
    "Khaki": (90.33, -9.01, 44.97),
    "PaleGoldenrod": (91.14, -7.35, 30.96),
    "LightGoldenrodYellow": (97.37, -6.48, 19.23),
    "LightYellow": (99.28, -5.1, 14.83),
    "Yellow": (97.14, -21.56, 94.48),
    "Gold": (86.93, -1.92, 87.14),
    "LightGoldenrod": (87.73, -6.26, 46.58),
    "Goldenrod": (70.82, 8.52, 68.76),
    "DarkGoldenrod": (59.22, 9.87, 62.73),
    "RosyBrown": (63.61, 17.02, 6.6),
    "IndianRed": (53.39, 44.84, 22.11),
    "SaddleBrown": (37.47, 26.45, 40.99),
    "Sienna": (43.8, 29.33, 35.64),
    "Peru": (61.75, 21.4, 47.92),
    "Burlywood": (77.02, 7.05, 30.01),
    "Beige": (95.95, -4.19, 12.04),
    "Wheat": (89.35, 1.51, 24.0),
    "SandyBrown": (73.95, 23.03, 46.79),
    "Tan": (74.97, 5.02, 24.42),
    "Chocolate": (55.99, 37.06, 56.74),
    "Firebrick": (39.11, 55.93, 37.65),
    "Brown": (37.52, 49.7, 30.54),
    "DarkSalmon": (69.85, 28.18, 27.7),
    "Salmon": (67.26, 45.23, 29.09),
    "LightSalmon": (74.7, 31.48, 34.54),
    "Orange": (74.93, 23.94, 78.96),
    "DarkOrange": (69.48, 36.83, 75.49),
    "Coral": (67.29, 45.36, 47.49),
    "LightCoral": (66.15, 42.82, 19.55),
    "Tomato": (62.2, 57.86, 46.42),
    "OrangeRed": (57.57, 67.8, 68.97),
    "Red": (53.23, 80.11, 67.22),
    "HotPink": (65.48, 64.25, -10.66),
    "DeepPink": (55.95, 84.56, -5.71),
    "Pink": (83.58, 24.15, 3.32),
    "LightPink": (81.05, 27.97, 5.03),
    "PaleVioletRed": (60.56, 45.53, 0.39),
    "Maroon": (41.51, 54.71, 2.46),
    "X11Maroon": (41.51, 54.71, 2.46),
    "WebMaroon": (25.53, 48.06, 38.06),
    "MediumVioletRed": (44.76, 71.01, -15.18),
    "VioletRed": (47.57, 72.25, -17.43),
    "Magenta": (60.32, 98.25, -60.84),
    "Fuchsia": (60.32, 98.25, -60.84),
    "Violet": (69.69, 56.37, -36.82),
    "Plum": (73.37, 32.54, -22.0),
    "Orchid": (62.8, 55.29, -34.42),
    "MediumOrchid": (53.64, 59.07, -47.41),
    "DarkOrchid": (43.38, 65.17, -60.11),
    "DarkViolet": (39.58, 76.34, -70.38),
    "BlueViolet": (42.19, 69.86, -74.77),
    "Purple": (45.36, 78.75, -77.41),
    "X11Purple": (45.36, 78.75, -77.41),
    "WebPurple": (29.78, 58.94, -36.5),
    "MediumPurple": (54.98, 36.81, -50.1),
    "Thistle": (80.08, 13.22, -9.24),
    "Snow1": (98.64, 1.66, 0.58),
    "Snow2": (92.72, 1.68, 0.59),
    "Snow3": (81.27, 1.39, 0.48),
    "Snow4": (57.26, 0.74, 0.26),
    "Seashell1": (97.12, 2.17, 4.54),
    "Seashell2": (91.46, 1.86, 4.48),
    "Seashell3": (80.0, 1.74, 3.99),
    "Seashell4": (56.24, 1.11, 2.81),
    "AntiqueWhite1": (95.21, 2.18, 11.6),
    "AntiqueWhite2": (89.54, 2.03, 11.14),
    "AntiqueWhite3": (78.35, 1.89, 9.7),
    "AntiqueWhite4": (55.15, 1.02, 7.02),
    "Bisque1": (92.01, 4.43, 19.0),
    "Bisque2": (86.6, 4.09, 18.0),
    "Bisque3": (75.65, 3.92, 15.59),
    "Bisque4": (53.19, 2.29, 11.77),
    "PeachPuff1": (89.35, 8.09, 21.01),
    "PeachPuff2": (83.92, 7.93, 19.54),
    "PeachPuff3": (73.42, 6.93, 17.36),
    "PeachPuff4": (51.41, 4.82, 12.77),
    "NavajoWhite1": (90.1, 4.51, 28.26),
    "NavajoWhite2": (84.68, 4.31, 26.89),
    "NavajoWhite3": (74.24, 3.46, 23.89),
    "NavajoWhite4": (51.81, 2.66, 17.38),
    "LemonChiffon1": (97.65, -5.42, 22.23),
    "LemonChiffon2": (91.78, -5.01, 21.06),
    "LemonChiffon3": (80.44, -4.53, 18.52),
    "LemonChiffon4": (56.63, -3.69, 13.7),
    "Cornsilk1": (97.46, -2.21, 14.28),
    "Cornsilk2": (91.82, -2.42, 13.86),
    "Cornsilk3": (80.44, -2.17, 12.13),
    "Cornsilk4": (56.54, -1.81, 8.99),
    "Ivory1": (99.64, -2.55, 7.15),
    "Ivory2": (93.76, -2.41, 6.76),
    "Ivory3": (82.1, -2.12, 5.96),
    "Ivory4": (57.65, -1.52, 4.27),
    "Honeydew1": (98.57, -7.56, 5.47),
    "Honeydew2": (92.74, -7.15, 5.17),
    "Honeydew3": (81.21, -6.3, 4.56),
    "Honeydew4": (57.01, -4.51, 3.26),
    "LavenderBlush1": (96.07, 5.89, -0.6),
    "LavenderBlush2": (90.39, 5.63, -0.73),
    "LavenderBlush3": (79.13, 4.91, -0.5),
    "LavenderBlush4": (55.53, 3.58, -0.54),
    "MistyRose1": (92.66, 8.75, 4.83),
    "MistyRose2": (87.2, 8.17, 4.63),
    "MistyRose3": (76.18, 7.5, 3.87),
    "MistyRose4": (53.59, 4.98, 3.03),
    "Azure1": (98.93, -4.88, -1.7),
    "Azure2": (93.09, -4.61, -1.61),
    "Azure3": (81.52, -4.06, -1.42),
    "Azure4": (57.23, -2.91, -1.02),
    "SlateBlue1": (55.5, 43.58, -69.43),
    "SlateBlue2": (51.85, 41.46, -65.91),
    "SlateBlue3": (45.02, 36.43, -58.3),
    "SlateBlue4": (30.49, 26.47, -42.65),
    "RoyalBlue1": (53.55, 29.71, -72.75),
    "RoyalBlue2": (50.12, 28.04, -68.87),
    "RoyalBlue3": (43.5, 24.47, -60.91),
    "RoyalBlue4": (29.32, 17.5, -44.65),
    "Blue1": (32.3, 79.2, -107.86),
    "Blue2": (29.84, 75.17, -102.38),
    "Blue3": (24.98, 67.18, -91.5),
    "Blue4": (14.76, 50.43, -68.68),
    "DodgerBlue1": (59.38, 9.97, -63.39),
    "DodgerBlue2": (55.55, 9.51, -60.16),
    "DodgerBlue3": (48.38, 7.73, -53.09),
    "DodgerBlue4": (32.75, 5.26, -39.16),
    "SteelBlue1": (72.33, -5.0, -42.76),
    "SteelBlue2": (67.99, -5.0, -40.35),
    "SteelBlue3": (59.2, -4.51, -35.85),
    "SteelBlue4": (40.84, -3.27, -26.29),
    "DeepSkyBlue1": (72.55, -17.65, -42.55),
    "DeepSkyBlue2": (68.03, -16.73, -40.4),
    "DeepSkyBlue3": (59.45, -15.58, -35.57),
    "DeepSkyBlue4": (40.84, -12.06, -26.38),
    "SkyBlue1": (79.91, -9.45, -30.9),
    "SkyBlue2": (75.02, -8.82, -29.33),
    "SkyBlue3": (65.65, -8.34, -25.77),
    "SkyBlue4": (45.51, -5.68, -18.98),
    "LightSkyBlue1": (87.41, -9.43, -19.27),
    "LightSkyBlue2": (82.19, -9.03, -18.22),
    "LightSkyBlue3": (71.91, -8.23, -16.07),
    "LightSkyBlue4": (50.12, -5.69, -11.85),
    "SlateGray1": (88.74, -3.11, -17.13),
    "SlateGray2": (83.48, -2.92, -16.15),
    "SlateGray3": (73.05, -2.84, -14.24),
    "SlateGray4": (50.94, -1.79, -10.53),
    "LightSteelBlue1": (88.75, -1.4, -17.1),
    "LightSteelBlue2": (83.42, -1.49, -16.23),
    "LightSteelBlue3": (72.98, -1.37, -14.32),
    "LightSteelBlue4": (51.09, -1.12, -10.29),
    "LightBlue1": (91.7, -11.82, -12.75),
    "LightBlue2": (86.21, -11.22, -12.11),
    "LightBlue3": (75.44, -9.71, -10.7),
    "LightBlue4": (52.99, -7.69, -7.49),
    "LightCyan1": (97.87, -9.94, -3.38),
    "LightCyan2": (92.08, -9.42, -3.21),
    "LightCyan3": (80.61, -8.35, -2.85),
    "LightCyan4": (56.55, -6.11, -2.08),
    "PaleTurquoise1": (95.71, -20.9, -6.81),
    "PaleTurquoise2": (90.01, -19.92, -6.49),
    "PaleTurquoise3": (78.78, -17.62, -5.75),
    "PaleTurquoise4": (55.23, -12.78, -4.18),
    "CadetBlue1": (91.32, -25.16, -13.51),
    "CadetBlue2": (85.99, -23.94, -12.64),
    "CadetBlue3": (75.13, -21.2, -11.34),
    "CadetBlue4": (52.68, -15.69, -8.09),
    "Turquoise1": (88.22, -43.72, -18.49),
    "Turquoise2": (83.03, -41.66, -17.38),
    "Turquoise3": (72.46, -37.15, -15.62),
    "Turquoise4": (50.59, -28.18, -11.44),
    "Cyan1": (91.12, -48.08, -14.14),
    "Cyan2": (85.67, -45.63, -13.42),
    "Cyan3": (74.87, -40.79, -11.99),
    "Cyan4": (52.21, -30.62, -9.0),
    "DarkSlateGray1": (94.02, -30.19, -9.5),
    "DarkSlateGray2": (88.44, -28.55, -8.99),
    "DarkSlateGray3": (77.36, -25.44, -8.01),
    "DarkSlateGray4": (54.16, -18.65, -5.89),
    "Aquamarine1": (92.04, -45.52, 9.71),
    "Aquamarine2": (86.54, -43.16, 9.07),
    "Aquamarine3": (75.69, -38.33, 8.3),
    "Aquamarine4": (52.94, -27.92, 5.57),
    "DarkSeaGreen1": (94.61, -30.96, 23.5),
    "DarkSeaGreen2": (88.99, -29.35, 22.27),
    "DarkSeaGreen3": (77.87, -26.02, 19.74),
    "DarkSeaGreen4": (54.54, -19.03, 14.4),
    "SeaGreen1": (89.82, -64.47, 33.42),
    "SeaGreen2": (84.44, -61.17, 31.76),
    "SeaGreen3": (73.81, -54.27, 27.82),
    "SeaGreen4": (51.54, -39.71, 20.05),
    "PaleGreen1": (92.01, -49.1, 39.19),
    "PaleGreen2": (86.55, -46.33, 36.94),
    "PaleGreen3": (75.7, -41.09, 32.73),
    "PaleGreen4": (52.94, -30.05, 23.84),
    "SpringGreen1": (88.47, -76.9, 47.03),
    "SpringGreen2": (83.16, -73.0, 44.67),
    "SpringGreen3": (72.64, -65.04, 39.32),
    "SpringGreen4": (50.56, -48.48, 28.51),
    "Green1": (87.74, -86.18, 83.18),
    "Green2": (82.46, -81.8, 78.95),
    "Green3": (72.0, -73.11, 70.56),
    "Green4": (50.06, -54.88, 52.97),
    "Chartreuse1": (89.87, -68.07, 85.78),
    "Chartreuse2": (84.48, -64.63, 81.41),
    "Chartreuse3": (73.86, -57.39, 72.83),
    "Chartreuse4": (51.53, -42.45, 54.76),
    "OliveDrab1": (93.05, -45.04, 79.24),
    "OliveDrab2": (87.5, -42.7, 74.97),
    "OliveDrab3": (76.54, -37.99, 66.59),
    "OliveDrab4": (53.58, -27.66, 48.97),
    "DarkOliveGreen1": (93.99, -38.04, 61.76),
    "DarkOliveGreen2": (88.37, -36.24, 58.6),
    "DarkOliveGreen3": (77.33, -32.09, 51.78),
    "DarkOliveGreen4": (54.15, -23.42, 37.84),
    "Khaki1": (95.65, -10.81, 50.43),
    "Khaki2": (90.07, -10.49, 48.04),
    "Khaki3": (78.81, -9.22, 42.31),
    "Khaki4": (55.16, -6.66, 30.75),
    "LightGoldenrod1": (93.06, -6.24, 49.15),
    "LightGoldenrod2": (87.47, -5.75, 46.27),
    "LightGoldenrod3": (76.66, -5.39, 41.15),
    "LightGoldenrod4": (53.72, -4.1, 30.02),
    "LightYellow1": (99.28, -5.1, 14.83),
    "LightYellow2": (93.42, -4.84, 14.05),
    "LightYellow3": (81.8, -4.29, 12.46),
    "LightYellow4": (57.42, -3.14, 9.1),
    "Yellow1": (97.14, -21.56, 94.48),
    "Yellow2": (91.38, -20.46, 89.68),
    "Yellow3": (79.98, -18.29, 80.15),
    "Yellow4": (56.04, -13.73, 60.16),
    "Gold1": (86.93, -1.92, 87.14),
    "Gold2": (81.81, -2.07, 82.79),
    "Gold3": (71.46, -1.93, 74.02),
    "Gold4": (49.75, -1.65, 55.63),
    "Goldenrod1": (81.58, 9.83, 77.88),
    "Goldenrod2": (76.64, 9.29, 73.88),
    "Goldenrod3": (66.91, 8.11, 65.78),
    "Goldenrod4": (46.5, 5.66, 48.4),
    "DarkGoldenrod1": (79.61, 13.63, 80.5),
    "DarkGoldenrod2": (74.89, 12.64, 76.39),
    "DarkGoldenrod3": (65.36, 11.05, 68.13),
    "DarkGoldenrod4": (45.38, 7.7, 50.7),
    "RosyBrown1": (83.57, 22.2, 8.65),
    "RosyBrown2": (78.53, 21.04, 8.2),
    "RosyBrown3": (68.6, 18.64, 7.25),
    "RosyBrown4": (47.77, 13.59, 5.27),
    "IndianRed1": (63.84, 56.76, 29.24),
    "IndianRed2": (59.89, 53.65, 27.56),
    "IndianRed3": (51.99, 47.63, 24.36),
    "IndianRed4": (35.64, 34.54, 17.29),
    "Sienna1": (67.78, 43.45, 52.51),
    "Sienna2": (63.55, 41.21, 49.68),
    "Sienna3": (55.25, 36.55, 43.82),
    "Sienna4": (38.08, 26.14, 32.23),
    "Burlywood1": (87.1, 8.09, 33.52),
    "Burlywood2": (81.92, 7.64, 31.54),
    "Burlywood3": (71.7, 6.59, 27.98),
    "Burlywood4": (49.99, 4.92, 20.12),
    "Wheat1": (92.56, 1.56, 24.92),
    "Wheat2": (87.17, 1.32, 23.5),
    "Wheat3": (76.25, 1.2, 20.73),
    "Wheat4": (53.35, 0.95, 14.89),
    "Tan1": (75.29, 25.96, 56.81),
    "Tan2": (70.71, 24.47, 54.06),
    "Tan3": (61.75, 21.4, 47.92),
    "Tan4": (42.73, 15.5, 34.69),
    "Chocolate1": (66.95, 43.78, 66.34),
    "Chocolate2": (62.71, 41.6, 62.89),
    "Chocolate3": (54.63, 36.57, 55.68),
    "Chocolate4": (37.47, 26.45, 40.99),
    "Firebrick1": (55.67, 74.4, 51.52),
    "Firebrick2": (52.02, 70.63, 48.93),
    "Firebrick3": (44.95, 62.78, 43.03),
    "Firebrick4": (30.16, 46.18, 30.57),
    "Brown1": (57.36, 70.56, 44.82),
    "Brown2": (53.62, 66.99, 42.57),
    "Brown3": (46.43, 59.44, 37.38),
    "Brown4": (31.38, 43.46, 26.43),
    "Salmon1": (70.2, 40.42, 37.88),
    "Salmon2": (65.77, 38.54, 35.61),
    "Salmon3": (57.28, 34.04, 31.7),
    "Salmon4": (39.5, 24.64, 22.9),
    "LightSalmon1": (74.7, 31.48, 34.54),
    "LightSalmon2": (70.1, 29.93, 32.47),
    "LightSalmon3": (61.27, 26.09, 29.02),
    "LightSalmon4": (42.31, 19.12, 21.13),
    "Orange1": (74.93, 23.94, 78.96),
    "Orange2": (70.38, 22.55, 74.99),
    "Orange3": (61.44, 19.61, 67.18),
    "Orange4": (42.46, 13.96, 50.64),
    "DarkOrange1": (66.85, 43.32, 73.91),
    "DarkOrange2": (62.62, 41.16, 70.14),
    "DarkOrange3": (54.53, 36.13, 62.85),
    "DarkOrange4": (37.38, 26.03, 47.43),
    "Coral1": (64.94, 51.88, 41.62),
    "Coral2": (60.84, 49.22, 39.35),
    "Coral3": (52.83, 43.72, 34.62),
    "Coral4": (36.25, 31.62, 24.88),
    "Tomato1": (62.2, 57.86, 46.42),
    "Tomato2": (58.25, 54.87, 43.89),
    "Tomato3": (50.53, 48.72, 38.6),
    "Tomato4": (34.53, 35.2, 28.23),
    "OrangeRed1": (57.57, 67.8, 68.97),
    "OrangeRed2": (53.86, 64.26, 65.48),
    "OrangeRed3": (46.59, 57.02, 58.59),
    "OrangeRed4": (31.38, 41.72, 43.81),
    "Red1": (53.23, 80.11, 67.22),
    "Red2": (49.71, 76.03, 63.8),
    "Red3": (42.73, 67.96, 57.02),
    "Red4": (28.08, 51.01, 41.29),
    "DeepPink1": (55.95, 84.56, -5.71),
    "DeepPink2": (52.3, 80.25, -5.51),
    "DeepPink3": (45.16, 71.55, -5.24),
    "DeepPink4": (30.12, 53.45, -4.8),
    "HotPink1": (66.3, 62.07, -9.44),
    "HotPink2": (62.74, 57.08, -7.6),
    "HotPink3": (55.44, 48.37, -5.63),
    "HotPink4": (36.74, 39.02, -6.57),
    "Pink1": (80.93, 29.06, 2.69),
    "Pink2": (76.08, 27.45, 2.49),
    "Pink3": (66.29, 24.55, 2.25),
    "Pink4": (46.31, 17.59, 1.36),
    "LightPink1": (79.06, 31.07, 6.48),
    "LightPink2": (74.21, 29.63, 5.82),
    "LightPink3": (64.89, 25.98, 5.29),
    "LightPink4": (45.1, 18.84, 3.84),
    "PaleVioletRed1": (69.59, 51.68, 0.49),
    "PaleVioletRed2": (65.24, 48.96, 0.66),
    "PaleVioletRed3": (56.77, 43.5, 0.43),
    "PaleVioletRed4": (39.22, 31.45, 0.24),
    "Maroon1": (58.95, 82.2, -19.96),
    "Maroon2": (55.16, 78.0, -19.03),
    "Maroon3": (47.72, 69.51, -17.24),
    "Maroon4": (32.26, 51.35, -13.33),
    "VioletRed1": (58.89, 76.67, -3.15),
    "VioletRed2": (55.17, 72.57, -3.07),
    "VioletRed3": (47.77, 64.44, -2.61),
    "VioletRed4": (32.35, 47.49, -2.81),
    "Magenta1": (60.32, 98.25, -60.84),
    "Magenta2": (56.44, 93.25, -57.75),
    "Magenta3": (48.74, 83.35, -51.61),
    "Magenta4": (32.6, 62.56, -38.74),
    "Orchid1": (72.49, 62.7, -38.87),
    "Orchid2": (68.01, 59.38, -36.7),
    "Orchid3": (59.25, 52.73, -32.74),
    "Orchid4": (40.9, 38.74, -24.41),
    "Plum1": (83.98, 35.3, -23.9),
    "Plum2": (78.82, 33.66, -22.78),
    "Plum3": (68.9, 29.75, -20.15),
    "Plum4": (48.08, 21.49, -14.58),
    "MediumOrchid1": (63.81, 68.93, -55.54),
    "MediumOrchid2": (59.81, 65.28, -52.62),
    "MediumOrchid3": (52.0, 57.81, -46.65),
    "MediumOrchid4": (35.47, 42.55, -34.34),
    "DarkOrchid1": (53.75, 77.93, -71.94),
    "DarkOrchid2": (50.29, 73.68, -68.13),
    "DarkOrchid3": (43.59, 65.55, -60.33),
    "DarkOrchid4": (29.29, 48.02, -44.38),
    "Purple1": (47.37, 76.94, -82.55),
    "Purple2": (44.22, 73.15, -78.21),
    "Purple3": (38.12, 64.97, -69.43),
    "Purple4": (25.36, 47.7, -50.89),
    "MediumPurple1": (63.21, 41.89, -56.85),
    "MediumPurple2": (59.18, 39.62, -53.97),
    "MediumPurple3": (51.41, 35.19, -47.89),
    "MediumPurple4": (35.4, 25.25, -34.67),
    "Thistle1": (92.72, 15.38, -10.74),
    "Thistle2": (87.21, 14.55, -10.16),
    "Thistle3": (76.34, 12.82, -8.96),
    "Thistle4": (53.51, 9.18, -6.42),
    "Gray0": (0.0, 0.0, 0.0),
    "Gray1": (0.82, 0.0, -0.0),
    "Gray2": (1.37, 0.0, -0.0),
    "Gray3": (2.19, 0.0, -0.0),
    "Gray4": (2.74, 0.0, -0.0),
    "Gray5": (3.64, 0.0, -0.0),
    "Gray6": (4.31, 0.0, -0.0),
    "Gray7": (5.46, 0.0, -0.0),
    "Gray8": (6.32, 0.0, -0.0),
    "Gray9": (7.74, 0.0, -0.0),
    "Gray10": (9.26, 0.0, -0.0),
    "Gray11": (10.27, 0.0, -0.0),
    "Gray12": (11.76, 0.0, -0.0),
    "Gray13": (12.74, 0.0, -0.0),
    "Gray14": (14.2, 0.0, -0.0),
    "Gray15": (15.16, 0.0, -0.0),
    "Gray16": (16.59, 0.0, -0.0),
    "Gray17": (17.53, 0.0, -0.0),
    "Gray18": (18.94, 0.0, -0.0),
    "Gray19": (19.87, 0.0, -0.0),
    "Gray20": (21.25, 0.0, -0.0),
    "Gray21": (22.62, 0.0, -0.0),
    "Gray22": (23.52, 0.0, -0.0),
    "Gray23": (24.87, 0.0, -0.0),
    "Gray24": (25.76, 0.0, -0.0),
    "Gray25": (27.09, 0.0, -0.0),
    "Gray26": (27.97, 0.0, -0.0),
    "Gray27": (29.29, 0.0, -0.0),
    "Gray28": (30.16, 0.0, -0.0),
    "Gray29": (31.46, 0.0, -0.0),
    "Gray30": (32.75, 0.0, -0.0),
    "Gray31": (33.6, 0.0, -0.0),
    "Gray32": (34.88, 0.0, -0.0),
    "Gray33": (35.72, 0.0, -0.0),
    "Gray34": (36.99, 0.0, -0.0),
    "Gray35": (37.82, 0.0, -0.0),
    "Gray36": (39.07, 0.0, -0.0),
    "Gray37": (39.9, 0.0, -0.01),
    "Gray38": (41.14, 0.0, -0.01),
    "Gray39": (41.96, 0.0, -0.01),
    "Gray40": (43.19, 0.0, -0.01),
    "Gray41": (44.41, 0.0, -0.01),
    "Gray42": (45.22, 0.0, -0.01),
    "Gray43": (46.44, 0.0, -0.01),
    "Gray44": (47.24, 0.0, -0.01),
    "Gray45": (48.44, 0.0, -0.01),
    "Gray46": (49.24, 0.0, -0.01),
    "Gray47": (50.43, 0.0, -0.01),
    "Gray48": (51.22, 0.0, -0.01),
    "Gray49": (52.41, 0.0, -0.01),
    "Gray50": (53.19, 0.0, -0.01),
    "Gray51": (54.37, 0.0, -0.01),
    "Gray52": (55.54, 0.0, -0.01),
    "Gray53": (56.32, 0.0, -0.01),
    "Gray54": (57.48, 0.0, -0.01),
    "Gray55": (58.25, 0.0, -0.01),
    "Gray56": (59.4, 0.0, -0.01),
    "Gray57": (60.17, 0.0, -0.01),
    "Gray58": (61.32, 0.0, -0.01),
    "Gray59": (62.08, 0.0, -0.01),
    "Gray60": (63.22, 0.0, -0.01),
    "Gray61": (64.36, 0.0, -0.01),
    "Gray62": (65.11, 0.0, -0.01),
    "Gray63": (66.24, 0.0, -0.01),
    "Gray64": (66.99, 0.0, -0.01),
    "Gray65": (68.12, 0.0, -0.01),
    "Gray66": (68.87, 0.0, -0.01),
    "Gray67": (69.98, 0.0, -0.01),
    "Gray68": (70.72, 0.0, -0.01),
    "Gray69": (71.84, 0.0, -0.01),
    "Gray70": (72.94, 0.0, -0.01),
    "Gray71": (73.68, 0.0, -0.01),
    "Gray72": (74.78, 0.0, -0.01),
    "Gray73": (75.51, 0.0, -0.01),
    "Gray74": (76.61, 0.0, -0.01),
    "Gray75": (77.34, 0.0, -0.01),
    "Gray76": (78.43, 0.0, -0.01),
    "Gray77": (79.16, 0.0, -0.01),
    "Gray78": (80.24, 0.0, -0.01),
    "Gray79": (80.97, 0.0, -0.01),
    "Gray80": (82.05, 0.0, -0.01),
    "Gray81": (83.12, 0.0, -0.01),
    "Gray82": (83.84, 0.0, -0.01),
    "Gray83": (84.91, 0.0, -0.01),
    "Gray84": (85.63, 0.0, -0.01),
    "Gray85": (86.7, 0.0, -0.01),
    "Gray86": (87.41, 0.0, -0.01),
    "Gray87": (88.47, 0.0, -0.01),
    "Gray88": (89.18, 0.0, -0.01),
    "Gray89": (90.24, 0.0, -0.01),
    "Gray90": (90.94, 0.0, -0.01),
    "Gray91": (92.0, 0.0, -0.01),
    "Gray92": (93.05, 0.0, -0.01),
    "Gray93": (93.75, 0.0, -0.01),
    "Gray94": (94.8, 0.01, -0.01),
    "Gray95": (95.49, 0.01, -0.01),
    "Gray96": (96.54, 0.01, -0.01),
    "Gray97": (97.23, 0.01, -0.01),
    "Gray98": (98.27, 0.01, -0.01),
    "Gray99": (98.96, 0.01, -0.01),
    "Gray100": (100.0, 0.01, -0.01),
    "DarkGray": (69.24, 0.0, -0.01),
    "DarkBlue": (14.76, 50.43, -68.68),
    "DarkCyan": (52.21, -30.62, -9.0),
    "DarkMagenta": (32.6, 62.56, -38.74),
    "DarkRed": (28.08, 51.01, 41.29),
    "LightGreen": (86.55, -46.33, 36.94),
    "Crimson": (47.03, 70.94, 33.59),
    "Indigo": (20.47, 51.69, -53.32),
    "Olive": (51.87, -12.93, 56.68),
    "RebeccaPurple": (32.9, 42.89, -47.16),
    "Silver": (77.7, 0.0, -0.01),
    "Teal": (48.26, -28.84, -8.48),
}


def classify_pixel_hsv(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h_deg = h * 360
    if v < 0.22: return "Black", s
    if v > 0.82 and s < 0.06: return "White", s
    if s < 0.15: return "Gray", s 
    if h_deg < 10 or h_deg >= 345: 
        res = "Brown" if v < 0.15 else "Red"
    elif 10 <= h_deg < 42: 
        res = "Brown" if (v < 0.82 and s < 0.78) or (v < 0.6) else "Orange"
    elif 42 <= h_deg < 75: res = "Yellow"
    elif 75 <= h_deg < 165: res = "Green"
    elif 165 <= h_deg < 205: res = "Cyan"
    elif 205 <= h_deg < 245: res = "Blue"
    elif 245 <= h_deg < 290: res = "Purple"
    else: res = "Pink"
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
        weight = 1.0 if name in ["Black", "White", "Gray"] else (1.0 + sat * 1.5)
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
    if core_img.mode == 'RGBA':
        core_pixels = [tuple(p[:3]) for p in np.asarray(core_img).reshape(-1, 4) if p[3] > 0]
    else:
        core_pixels = np.asarray(core_img.convert('RGB')).reshape(-1, 3)
    if not core_pixels: return None
    return engine_saliency(core_pixels)

def engine_bg_purger(image):
    """Engine 4: Tu dong loai bo mau nen o ria anh"""
    w, h = image.size
    edge_pixels = []
    is_rgba = (image.mode == 'RGBA')
    img_data = image.load()
    for x in [0, w-1]:
        for y in range(h):
            p = img_data[x, y]
            if not is_rgba or p[3] > 0: edge_pixels.append(p[:3] if is_rgba else p)
    for y in [0, h-1]:
        for x in range(w):
            p = img_data[x, y]
            if not is_rgba or p[3] > 0: edge_pixels.append(p[:3] if is_rgba else p)
    
    bg_color = None
    if edge_pixels:
        bg_counts = collections.Counter([classify_pixel_hsv(p)[0] for p in edge_pixels])
        bg_color = bg_counts.most_common(1)[0][0]
    
    if is_rgba:
        pixels = [tuple(p[:3]) for p in np.asarray(image).reshape(-1, 4) if p[3] > 0]
    else:
        pixels = np.asarray(image.convert('RGB')).reshape(-1, 3)
        
    scores = collections.defaultdict(float)
    for p in pixels:
        name, sat = classify_pixel_hsv(p)
        weight = 0.5 if name == bg_color else (1.0 + sat * 1.5)
        scores[name] += weight
    return max(scores, key=scores.get) if scores else None

def engine_palette_cluster(image, clusters=4, iterations=6):
    """Engine 5: Phan cum bang K-Means de tim mau chu dao"""
    is_rgba = (image.mode == 'RGBA')
    if is_rgba:
        pixels = np.array([p[:3] for p in np.asarray(image).reshape(-1, 4) if p[3] > 0], dtype=np.float32)
    else:
        pixels = np.asarray(image.convert("RGB"), dtype=np.float32).reshape(-1, 3)
        
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
        neutral_penalty = 0.6 if name in ["Black", "White", "Gray"] else 1.0
        scores[name] += cluster_ratio * (1.0 + sat * 1.8) * neutral_penalty

    return max(scores, key=scores.get) if scores else None

def engine_lab_distance(image):
    """Engine 6: So mau trung binh voi bang mau tham chieu bang LAB/Delta E"""
    is_rgba = (image.mode == 'RGBA')
    if is_rgba:
        pixels = np.array([p[:3] for p in np.asarray(image).reshape(-1, 4) if p[3] > 0], dtype=np.float32)
    else:
        pixels = np.asarray(image.convert("RGB"), dtype=np.float32).reshape(-1, 3)
        
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
    # Khong convert RGB de giu lai Alpha neu co
    if image.mode != 'RGBA':
        image = image.convert('RGB')
        
    image_thumb = image.copy()
    image_thumb.thumbnail((100, 100))
    
    if image_thumb.mode == 'RGBA':
        pixels = [tuple(p[:3]) for p in np.asarray(image_thumb).reshape(-1, 4) if p[3] > 0]
    else:
        pixels = [tuple(p) for p in np.asarray(image_thumb).reshape(-1, 3)]
        
    if not pixels:
        # Fallback pseudo result if empty selection
        return [{"name": "Black", "hex": "#000000", "confidence": 100}]
    
    # Thu thap ket qua tu cac chuyen gia
    votes = []
    votes.append(engine_saliency(pixels))
    votes.append(engine_most_frequent(pixels))
    votes.append(engine_core_focus(image_thumb))
    votes.append(engine_bg_purger(image_thumb))
    votes.append(engine_palette_cluster(image_thumb))
    votes.append(engine_lab_distance(image_thumb))
    
    # Loai bo cac vote None
    votes = [v for v in votes if v is not None]
    if not votes:
        votes = ["Black"]
    
    # Dem phieu
    vote_counts = collections.Counter(votes)
    winner, win_count = vote_counts.most_common(1)[0]
    
    # He thong uu tien:
    final_color = winner if win_count >= 2 else votes[0]
    
    # Tim top mau phu dua tren tan suat pixel
    pixels_flat = [classify_pixel_hsv(p)[0] for p in pixels]
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

# --- CHUC NANG KHOANH VUNG (LASSO) ---

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
    overlay.attributes('-topmost', True)
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
        # Dong đa giác
        px, py = lasso_points[-1]
        fx, fy = lasso_points[0]
        lasso_canvas.create_line(px, py, fx, fy, fill="#FF00FF", width=2, tags="lasso_line")
        
        # Xử lý vùng vẽ
        try:
            # Tao mask tu polygon
            mask = Image.new('L', lasso_screenshot.size, 0)
            ImageDraw.Draw(mask).polygon(lasso_points, fill=255)
            
            # Ghep mask vao anh
            rgba_img = lasso_screenshot.convert('RGBA')
            rgba_img.putalpha(mask)
            
            # Cat (crop) theo bounding box
            xs = [p[0] for p in lasso_points]
            ys = [p[1] for p in lasso_points]
            bbox = (min(xs), min(ys), max(xs), max(ys))
            cropped_img = rgba_img.crop(bbox)
            
            cleanup_lasso()
            render_analysis(cropped_img)
        except Exception as e:
            print(f"Lỗi xử lý lasso: {e}")
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
        try:
            lasso_overlay.destroy()
        except: pass
    lasso_overlay = lasso_canvas = lasso_screenshot = lasso_tk_img = None
    app.deiconify()
    app.lift()
    app.focus_force()
    
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
            import traceback
            err_msg = traceback.format_exc()
            # Log loi ra file de debug
            try:
                log_path = os.path.join(get_app_dir(), "error.log")
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(f"\n--- Analysis Error ---\n{err_msg}\n")
            except Exception:
                pass
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
        result_color_box2.pack_forget()
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
        result_color_box3.pack_forget()
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
    result_color_box2.pack_forget()
    result_color_box3.pack_forget()
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

    enable_precision_mouse()

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
app.title("Color Picker v2.3")
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

# --- WIN32 HOTKEY LISTENER ---
def start_hotkey_listener():
    def listener():
        user32 = ctypes.windll.user32
        MOD_ALT = 0x0001
        VK_S = 0x53
        VK_X = 0x58
        VK_A = 0x41
        
        # RegisterHotKey(hWnd, id, fsModifiers, vk)
        # ID 1 for Alt+S, ID 2 for Alt+X, ID 3 for Alt+A
        user32.RegisterHotKey(None, 1, MOD_ALT, VK_S)
        user32.RegisterHotKey(None, 2, MOD_ALT, VK_X)
        user32.RegisterHotKey(None, 3, MOD_ALT, VK_A)

        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312: # WM_HOTKEY
                    if msg.wParam == 1:
                        app.after(0, start_eyedropper)
                    elif msg.wParam == 3:
                        app.after(0, start_lasso)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
            user32.UnregisterHotKey(None, 2)
            user32.UnregisterHotKey(None, 3)

    threading.Thread(target=listener, daemon=True).start()

if __name__ == "__main__":
    single_instance_check()
    start_hotkey_listener()
    app.mainloop()
