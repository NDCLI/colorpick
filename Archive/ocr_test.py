import pytesseract
from PIL import Image
import os

try:
    img = Image.open('mamau.jpg')
    text = pytesseract.image_to_string(img)
    print("OCR extracted length:", len(text))
    print(text[:500])
except Exception as e:
    print("OCR Failed:", e)
