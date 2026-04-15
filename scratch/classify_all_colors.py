"""
Classify all X11 colors into 11 families using AI-derived logic.
v4: Two-column layout (5 groups in Col 1, 6 groups in Col 2).
"""
import json
import colorsys
from PIL import Image, ImageDraw, ImageFont
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

with open(os.path.join(PROJECT_DIR, "Archive", "x11_colors.json"), "r") as f:
    X11_COLORS = json.load(f)


def hex_to_rgb(hex_code):
    h = hex_code.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def ai_classify(hex_code):
    """
    Classify a hex color into one of 11 families.
    v3: Updated Pink threshold to catch Rose tones.
    """
    r, g, b = hex_to_rgb(hex_code)
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h_deg = h * 360

    # --- ACHROMATIC ---
    if v < 0.15:
        return "Black"
    if v > 0.90 and s < 0.06:
        return "White"
    if v > 0.85 and s < 0.08:
        return "White"
    if s < 0.05:
        if v >= 0.80:
            return "White"
        if v <= 0.20:
            return "Black"
        return "Gray"
    if s < 0.10:
        if v >= 0.88:
            return "White"
        if v <= 0.22:
            return "Black"
        return "Gray"

    # == RED zone ==
    if h_deg >= 345 or h_deg < 12:
        if s < 0.36 and v > 0.75:
            return "Pink"
        if v < 0.35:
            return "Brown" if h_deg < 10 else "Red"
        if v < 0.55 and s > 0.50:
            return "Brown"
        return "Red"

    # == PINK ==
    if h_deg >= 295:
        if v < 0.45:
            return "Purple"
        if h_deg < 315 and v < 0.65 and s > 0.50:
            return "Purple"
        return "Pink"

    # == ORANGE + BROWN ==
    if h_deg < 45:
        if v < 0.45:
            return "Brown"
        if v < 0.65:
            if s > 0.60:
                return "Orange" if v > 0.55 else "Brown"
            return "Brown"
        if s < 0.25 and v < 0.82:
            return "Brown"
        return "Orange"

    # == YELLOW ==
    if h_deg < 70:
        if v < 0.40 and h_deg < 60:
            return "Brown"
        if v < 0.58 and s < 0.45 and h_deg < 60:
            return "Brown"
        if h_deg > 60 and s > 0.50 and v < 0.50:
            return "Green"
        return "Yellow"

    # == YELLOW-GREEN ==
    if h_deg < 85:
        if s > 0.30:
            return "Green"
        return "Yellow"

    # == GREEN ==
    if h_deg < 170:
        return "Green"

    # == BLUE ==
    if h_deg < 245:
        return "Blue"

    # == PURPLE ==
    if h_deg < 315:
        if h_deg > 300 and s < 0.20 and v > 0.80:
            return "Pink"
        return "Purple"

    return "Gray"


# =========================================
# CLASSIFY ALL
# =========================================
families = {
    "Red": [], "Orange": [], "Yellow": [], "Green": [], "Blue": [],
    "Purple": [], "Pink": [], "Brown": [], "White": [], "Gray": [], "Black": []
}

for name, hex_val in X11_COLORS.items():
    family = ai_classify(hex_val)
    families[family].append((name, hex_val.upper()))

def sort_dark_to_light(item):
    _, hex_val = item
    r, g, b = hex_to_rgb(hex_val)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (v, -s)

for family in families:
    families[family].sort(key=sort_dark_to_light)

# =========================================
# GENERATE IMAGE (3-Column Layout)
# =========================================
COL1 = ["Red", "Orange", "Yellow", "Green"]
COL2 = ["Blue", "Purple", "Pink", "Brown"]
COL3 = ["White", "Gray", "Black"]

FAMILY_HEADER_COLORS = {
    "Red": "#C0392B", "Orange": "#E67E22", "Yellow": "#F1C40F",
    "Green": "#27AE60", "Blue": "#2980B9", "Purple": "#8E44AD",
    "Pink": "#FF69B4", "Brown": "#795548", "White": "#BBBBBB",
    "Gray": "#7F8C8D", "Black": "#2C3E50"
}

SWATCH_W = 56
SWATCH_H = 26
COLS_PER_GROUP = 7 # Slightly narrower groups to fit 3 columns nicely
PAD = 20
HEADER_H = 32
FAMILY_GAP = 20
LABEL_H = 12

img_col_w = COLS_PER_GROUP * (SWATCH_W + 2) + PAD
img_w = PAD + (img_col_w * 3) + PAD

try:
    font_hdr = ImageFont.truetype("arial.ttf", 14)
    font_hex = ImageFont.truetype("arial.ttf", 9)
except:
    font_hdr = ImageFont.load_default()
    font_hex = ImageFont.load_default()

def generate_chart(output_path, show_hex=True):
    h1 = calculate_col_height(COL1, show_hex)
    h2 = calculate_col_height(COL2, show_hex)
    h3 = calculate_col_height(COL3, show_hex)
    img_h_val = max(h1, h2, h3) + PAD

    img_obj = Image.new("RGB", (img_w, img_h_val), "#1A1A2E")
    draw_obj = ImageDraw.Draw(img_obj)

    title = "X11 Color Families - 3 Column Layout" + (" (Hex)" if show_hex else " (Clean)")
    draw_obj.text((PAD, 10), title, fill="#FFF", font=font_hdr)

    def draw_column_internal(draw_ptr, col_families, start_x, start_y):
        current_y = start_y
        for family_name in col_families:
            colors = families[family_name]
            count = len(colors)
            hdr_c = FAMILY_HEADER_COLORS[family_name]

            # Header
            draw_ptr.rounded_rectangle([start_x, current_y, start_x + 160, current_y + HEADER_H - 4], radius=6, fill=hdr_c)
            hr, hg, hb = hex_to_rgb(hdr_c)
            tc = "#000" if (hr * 0.299 + hg * 0.587 + hb * 0.114) > 140 else "#FFF"
            draw_ptr.text((start_x + 10, current_y + 8), f"{family_name} ({count})", fill=tc, font=font_hdr)
            current_y += HEADER_H
            
            inner_x = start_x
            col_count = 0
            for name, hex_val in colors:
                draw_ptr.rectangle([inner_x, current_y, inner_x + SWATCH_W, current_y + SWATCH_H], fill=hex_val, outline="#333")
                
                if show_hex:
                    lr, lg, lb = hex_to_rgb(hex_val)
                    lum = lr * 0.299 + lg * 0.587 + lb * 0.114
                    label_c = "#000" if lum > 140 else "#FFF"
                    draw_ptr.text((inner_x + 2, current_y + SWATCH_H - 11), hex_val, fill=label_c, font=font_hex)

                inner_x += SWATCH_W + 2
                col_count += 1
                if col_count >= COLS_PER_GROUP:
                    col_count = 0
                    inner_x = start_x
                    current_y += SWATCH_H + 3
            
            if col_count > 0:
                current_y += SWATCH_H + 3
            current_y += FAMILY_GAP

    draw_column_internal(draw_obj, COL1, PAD, 50)
    draw_column_internal(draw_obj, COL2, PAD + img_col_w, 50)
    draw_column_internal(draw_obj, COL3, PAD + img_col_w * 2, 50)
    
    img_obj.save(output_path, quality=95)
    print(f"Generated: {output_path}")

def calculate_col_height(col_families, show_hex):
    h = 50
    for f in col_families:
        n = len(families[f])
        rows = (n + COLS_PER_GROUP - 1) // COLS_PER_GROUP
        h += HEADER_H + 2 + rows * (SWATCH_H + 3) + FAMILY_GAP
    return h

out_hex = os.path.join(PROJECT_DIR, "scratch", "x11_color_families_v2.png")
out_clean = os.path.join(PROJECT_DIR, "scratch", "x11_color_families_clean.png")

generate_chart(out_hex, show_hex=True)
generate_chart(out_clean, show_hex=False)
