# pip install Pillow
# pip install pytesseract
# https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

import time, base64
from gtts import gTTS
from googletrans import Translator
from pytesseract import pytesseract
from PIL import Image
from io import BytesIO

class TraductorUtil:
    
    def __init__(self):
        pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def reconocer_texto(self, ruta_imagen):
        # imagen = Image.open(BytesIO(imagen_bytes))
        imagen = Image.open(ruta_imagen)
        text = str(pytesseract.image_to_string(imagen)).strip()
        return text
    
    def traducir_texto(self, texto, idioma_seleccionado):
        translator = Translator()
        translation = translator.translate(texto, dest=idioma_seleccionado)
        return translation.text

    def guardar_audio(self, texto_traducido, idioma_seleccionado):
        # Guardar la imagen en el sistema de archivos
        timestamp = int(time.time())
        ruta_archivo = f"uploads/audios/audio_{timestamp}.mp3"

        tts = gTTS(text=texto_traducido, lang=idioma_seleccionado)
        tts.save(ruta_archivo)
        return ruta_archivo

    def guardar_imagen(self, imagen_base64):
        imagen_bytes = base64.b64decode(imagen_base64)
        timestamp = int(time.time())
        # Guardar la imagen en el sistema de archivos
        ruta_archivo = f"uploads/photos/imagen_{timestamp}.png"
        with open(ruta_archivo, "wb") as f:
            f.write(imagen_bytes)
        return ruta_archivo
