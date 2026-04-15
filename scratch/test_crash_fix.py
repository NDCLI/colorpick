
import colorsys
import collections
import numpy as np

# Mocking the updated environment from V2.3
COLOR_HEX = {
    "Black": "#000000",
    "Yellow": "#FFFF00",
    "DarkYellow": "#9C9C00",
    "Green": "#00FF00",
}

def get_safe_hex(color_name):
    if color_name in COLOR_HEX:
        return COLOR_HEX[color_name]
    temp_name = color_name
    if temp_name.startswith("👤 ") or temp_name.startswith("👗 "):
        temp_name = temp_name[2:]
    if temp_name in COLOR_HEX:
        return COLOR_HEX[temp_name]
    if temp_name.startswith("Dark"):
        base_color = temp_name[4:]
        if base_color in COLOR_HEX:
            return COLOR_HEX[base_color]
    return "#000000"

def test_safety(name):
    print(f"Lookup for '{name}': {get_safe_hex(name)}")

print("Testing safe lookup:")
test_safety("Yellow")        # Direct
test_safety("DarkYellow")    # Direct (added)
test_safety("DarkYellowNonExist") # Base fallback to Yellow? Wait, my logic checks for exact string.
test_safety("DarkGreen")     # Logic fallback to Green (if DarkGreen removed/missing)
test_safety("👗 Yellow")     # Prefix removal
test_safety("Unknown")       # Default fallback

# Simulate the crash scenario
final_color = "DarkYellow"
try:
    hex_val = get_safe_hex(final_color)
    print(f"SUCCESS: Found hex for {final_color}: {hex_val}")
except KeyError:
    print(f"FAILED: KeyError for {final_color}")
