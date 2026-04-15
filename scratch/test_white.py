"""
Test script: Verify White detection in classify_pixel
Run from: c:\Users\HVV-AI33\Desktop\Box\ColorPicker
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import colorsys
import collections
import numpy as np

# -------- Copy classify_pixel moi (v2.4 fixed) --------
def classify_pixel(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h_deg = h * 360

    if v < 0.18:
        return "Black", s
    # White: very bright, low-to-medium saturation
    if v > 0.87 and s < 0.22:
        return "White", s
    # Supplementary White
    if v > 0.80 and s < 0.14:
        return "White", s
    # Gray
    if s < 0.14:
        if v < 0.32:
            return "Black", s
        return "Gray", s

    # Chromatic...
    if h_deg >= 165 and h_deg < 260:
        return "Blue", s
    return "Blue", s  # simplify for test

# -------- Test cases --------
test_pixels = [
    # (hex_desc,              R,   G,   B,  expected)
    ("#C1CED8 (picked point)", 193, 206, 216, "White"),
    ("Light blue shirt v=0.92 s=0.15", 200, 215, 235, "White"),
    ("Light blue shirt v=0.88 s=0.18", 195, 210, 225, "White"),
    ("Pure white #FFFFFF",    255, 255, 255, "White"),
    ("Near white #F0F4F8",    240, 244, 248, "White"),
    ("#2980B9 deep blue",      41, 128, 185, "Blue"),
    ("#95A5A6 gray",          149, 165, 166, "Gray"),
    ("Highlight v=0.95 s=0.12",242, 242, 255, "White"),
    ("Shirt bright v=0.90 s=0.20",190, 210, 230, "White"),
    ("Shirt mid v=0.75 s=0.30", 133, 163, 191, "Blue"),
]

print("=" * 55)
print(f"{'Pixel':<35} {'Got':<8} {'Exp':<8} {'OK?'}")
print("=" * 55)
all_pass = True
for desc, r, g, b, expected in test_pixels:
    result, sat = classify_pixel((r, g, b))
    ok = "✅" if result == expected else "❌"
    if result != expected:
        all_pass = False
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    print(f"{desc:<35} {result:<8} {expected:<8} {ok}  (v={v:.2f} s={s:.2f})")

print("=" * 55)
print(f"\n{'✅ TẤT CẢ PASS!' if all_pass else '❌ CÓ TEST FAIL!'}")

# Simulate near-white injection
print("\n--- Simulate near_white injection ---")
# Create fake pixel array resembling the shirt
sim_pixels = []
# 50% light blue (v~0.88, s~0.18) -> now White
for _ in range(500):
    sim_pixels.append([200, 215, 235])
# 30% medium blue -> Blue  
for _ in range(300):
    sim_pixels.append([41, 128, 185])
# 20% gray
for _ in range(200):
    sim_pixels.append([149, 165, 166])

px = np.array(sim_pixels)
px_flat = [classify_pixel(tuple(p))[0] for p in px]
px_counts = collections.Counter(px_flat)
total = len(px_flat)
print("Pixel distribution:")
for name, cnt in px_counts.most_common():
    print(f"  {name}: {cnt}/{total} = {cnt/total*100:.1f}%")
