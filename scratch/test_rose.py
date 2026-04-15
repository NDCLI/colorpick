import colorsys

def classify_pixel(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h_deg = h * 360
    if h_deg >= 345 or h_deg < 12:
        if s < 0.36 and v > 0.75:
            return "Pink"
        return "Red"
    return "Other"

test_rose = (228, 158, 154) # #E49E9A
print(f"#E49E9A classified as: {classify_pixel(test_rose)}")
