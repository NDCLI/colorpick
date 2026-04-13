import urllib.request
import json

def get_x11_colors():
    url = "https://gitlab.freedesktop.org/xorg/app/rgb/-/raw/master/rgb.txt"
    data = urllib.request.urlopen(url).read().decode('utf-8')
    
    extracted = {}
    for line in data.split('\n'):
        if not line or line.startswith('!'): continue
        parts = line.strip().split(maxsplit=3)
        if len(parts) >= 4:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            name = parts[3]
            if ' ' not in name:
                # If name is all lowercase, capitalize it so 'black' becomes 'Black'
                if name.islower():
                    name = name.capitalize()
                    
                if 'grey' in name.lower() and name.lower() != name:
                    pass 
                    
                hex_code = f"#{r:02X}{g:02X}{b:02X}"
                extracted[name] = hex_code
                
    final_extracted = {}
    for k, v in extracted.items():
        if 'grey' in k.lower() and k.replace('grey', 'gray').replace('Grey', 'Gray') in extracted:
            continue
        final_extracted[k] = v

    # Add missing ones manually if still missing
    for forced in ['Black', 'White', 'Gray', 'Brown', 'Red', 'Orange', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'Pink']:
        if forced not in final_extracted:
            final_extracted[forced] = "#000000" # dummy, just to be safe, but actually let's print if missing
            print(f"Warning: {forced} still missing!")

    with open('x11_colors.json', 'w', encoding='utf-8') as f:
        json.dump(final_extracted, f, indent=4)

if __name__ == "__main__":
    get_x11_colors()
