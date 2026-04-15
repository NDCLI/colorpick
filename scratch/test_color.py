
import colorsys
import collections
import numpy as np

# Mocking the updated constants and functions from V2.3
COLOR_HEX = {
    "Black": "#000000",
    "DarkGreen": "#006400",
    "DarkGreenOlive": "#44533D",
    "Green": "#00FF00",
}

LAB_REFERENCE = {
    "Black": (0.0, 0.0, 0.0),
    "DarkGreen": (36.2, -43.37, 41.86),
    "DarkGreenOlive": (33.46, -10.64, 11.00),
    "Green": (87.74, -86.18, 83.18),
    "DarkSlateGray": (31.26, -11.72, -3.73),
}

def classify_pixel_hsv(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h_deg = h * 360
    if v < 0.12: return "Black", s
    if v > 0.82 and s < 0.06: return "White", s
    if s < 0.12: return "Gray", s 
    prefix = "Dark" if v < 0.40 else ""
    if 75 <= h_deg < 165: res = "Green"
    else: res = "Other"
    
    if prefix and res != "Other": return prefix + res, s
    return res, s

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

def classify_ambiguous_pixel(rgb, threshold=15.0):
    hsv_name, _ = classify_pixel_hsv(rgb)
    lab_val = rgb_to_lab(rgb)
    distances = []
    for name, ref_lab in LAB_REFERENCE.items():
        dist = delta_e(lab_val, ref_lab)
        distances.append((name, dist))
    distances.sort(key=lambda x: x[1])
    best_lab_name, best_dist = distances[0]
    results = [hsv_name]
    if best_lab_name not in results:
        results.append(best_lab_name)
    if len(results) < 2 and len(distances) > 1:
        second_lab_name, second_dist = distances[1]
        if second_dist - best_dist < threshold:
            results.append(second_lab_name)
    return results[:2]

def test_ambiguity(rgb, label):
    print(f"Testing {label} RGB: {rgb}")
    matches = classify_ambiguous_pixel(rgb)
    print(f"Matches: {' / '.join(matches)}")

# Test 1: Dark Green Olive (should be DarkGreen / DarkGreenOlive)
test_ambiguity((68, 83, 61), "Dark Green Olive")

# Test 2: Near Black (should give 2 results if close)
test_ambiguity((30, 35, 30), "Near Black")
