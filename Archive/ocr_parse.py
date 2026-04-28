import pytesseract
from PIL import Image
import os
import re
import json

# Try to find tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_colors():
    try:
        img = Image.open('mamau.jpg')
        text = pytesseract.image_to_string(img)
        
        extracted_colors = {}
        for line in text.split('\n'):
            line = line.strip()
            # Regex to match: Name (r g b) #hex
            # Or Name #hex
            # Or just name and hex
            # We want to find: Name and Hex
            # Looks like: GhostWhite (248 248 255) #F8F8FF
            match = re.search(r'^([a-zA-Z0-9_]+)\s*(?:\([^)]*\))?\s*(#[a-fA-F0-9]{6})', line)
            if match:
                name = match.group(1).strip()
                hex_code = match.group(2).strip().upper()
                extracted_colors[name] = hex_code
            else:
                # Fallback for lines like: GhostWhite #F8F8FF or something
                match2 = re.search(r'([a-zA-Z0-9_]+).*?(#[a-fA-F0-9]{6})', line)
                if match2:
                    name = match2.group(1).strip()
                    hex_code = match2.group(2).strip().upper()
                    extracted_colors[name] = hex_code
                    
        print(f"Extracted {len(extracted_colors)} colors.")
        if len(extracted_colors) > 0:
            with open('extracted_colors.json', 'w', encoding='utf-8') as f:
                json.dump(extracted_colors, f, indent=4)
        else:
            print("Failed to extract colors. Raw output start:")
            print(text[:500])
    except Exception as e:
        print("OCR Error:", e)

if __name__ == '__main__':
    parse_colors()
