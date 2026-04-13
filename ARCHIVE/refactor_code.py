import json
import re

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

def generate_replacements():
    with open('x11_colors.json', 'r', encoding='utf-8') as f:
        col_json = json.load(f)
        
    color_hex_code = "COLOR_HEX = {\n"
    lab_ref_code = "LAB_REFERENCE = {\n"
    
    for name, hex_c in col_json.items():
        color_hex_code += f'    "{name}": "{hex_c}",\n'
        r = int(hex_c[1:3], 16)
        g = int(hex_c[3:5], 16)
        b = int(hex_c[5:7], 16)
        l, a, b_val = rgb_to_lab((r, g, b))
        lab_ref_code += f'    "{name}": ({round(l, 2)}, {round(a, 2)}, {round(b_val, 2)}),\n'
        
    color_hex_code += "}"
    lab_ref_code += "}"
    
    return color_hex_code, lab_ref_code

def modify_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    color_hex_code, lab_ref_code = generate_replacements()
    
    # Replace COLOR_HEX
    content = re.sub(r'COLOR_HEX = \{.*?^\}', color_hex_code, content, flags=re.MULTILINE | re.DOTALL)
    
    # Replace LAB_REFERENCE
    content = re.sub(r'LAB_REFERENCE = \{.*?^\}', lab_ref_code, content, flags=re.MULTILINE | re.DOTALL)
    
    # Also update classify_pixel_hsv strings to standard X11 names
    content = content.replace('"Black (Carbon)"', '"Black"')
    content = content.replace('"White (Coconut)"', '"White"')
    content = content.replace('"Gray (Silver)"', '"Gray"')
    content = content.replace('"Brown (Dark)"', '"Brown"')
    content = content.replace('"Red (Classic)"', '"Red"')
    content = content.replace('"Orange (Bright)"', '"Orange"')
    content = content.replace('"Yellow (Bright)"', '"Yellow"')
    content = content.replace('"Green (Emerald)"', '"Green"')
    content = content.replace('"Blue (Cyan)"', '"Cyan"')
    content = content.replace('"Blue (Classic)"', '"Blue"')
    content = content.replace('"Purple (Violet)"', '"Purple"')
    content = content.replace('"Pink (Fuchsia)"', '"Pink"')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    files = ["ColorPickerV2.2.pyw", "ColorPicker_v2.pyw"]
    for file in files:
        modify_file(file)
    print("Files successfully updated.")
