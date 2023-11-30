import base64, json, datetime, time
from flask import Flask, request, jsonify, send_file # pip install flask
from flask_cors import CORS # pip install flask_cors

#import pyttsx3 # pip install pyttsx3

from pytesseract import pytesseract #pip install pytesseract
# https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#from translate import Translator # pip install translate

from gtts import gTTS
from googletrans import Translator
from playsound import playsound

from PIL import Image # pip install Pillow
from io import BytesIO


app = Flask(__name__)
CORS(app)

@app.route('/cargar_imagen', methods=['POST'])
def cargar_imagen():
    imagen_base64 = request.json.get('imagen')
    usuario = request.json.get('usuario')

    if imagen_base64:
        try:
        
            imagen_bytes = base64.b64decode(imagen_base64)
            timestamp = int(time.time())
            # Guardar la imagen en el sistema de archivos
            nombre_archivo = f"uploads/photos/imagen_{timestamp}.png"
            with open(nombre_archivo, "wb") as f:
                f.write(imagen_bytes)

            # imagen = Image.open(BytesIO(imagen_bytes))
            imagen = Image.open(nombre_archivo)
            text = str(pytesseract.image_to_string(imagen)).strip()

            registrar_log(f"Usuario '{usuario}' ha cargado una foto.", f"Texto reconocido: {text}\nFoto: {nombre_archivo}")

            return jsonify({"texto_reconocido": text, "mensaje": "Imagen cargada correctamente", "nombre_archivo": nombre_archivo})
        except Exception as e:
            print('se ha producido una excepción: '+e)
            return jsonify({"mensaje": "intenta otra vez"})
            
    else:
        return jsonify({"mensaje": "No se proporcionó ninguna imagen en la solicitud"}), 400

# Ruta para reconocer texto de una imagen
@app.route('/traducir', methods=['POST'])
def traducir():
    
    try:
        text = request.json.get('texto')
        to_lang = request.json.get('idioma')
        usuario = request.json.get('usuario')

        if (text):
            translation = _traducir_texto(text, to_lang)
            audio_path = _guardar_audio(translation, to_lang)
            registrar_log(f"Usuario '{usuario}' ha realizado una traducción.", f"Texto: {text}\nTraducción: {translation}\nIdioma: {to_lang}\nAudio: {audio_path}")
            return send_file(audio_path, mimetype='audio/mp3')
        else:
            return jsonify({"error": "por favor indícame algo para traducir"})

    except Exception as e:
            print('se ha producido una excepción: '+e.__str__())
            return jsonify({"mensaje": "intenta otra vez"})

def _traducir_texto(texto, idioma_seleccionado):
    translator = Translator()
    translation = translator.translate(texto, dest=idioma_seleccionado)
    return translation.text

def _guardar_audio(texto_traducido, idioma_seleccionado):
    # Guardar la imagen en el sistema de archivos
    timestamp = int(time.time())
    nombre_archivo = f"uploads/audios/audio_{timestamp}.mp3"

    tts = gTTS(text=texto_traducido, lang=idioma_seleccionado)
    tts.save(nombre_archivo)

    return nombre_archivo

@app.route('/registro', methods=['POST'])
def registro():
    username = request.json.get('usuario')
    clave = request.json.get('clave')
    nombre = request.json.get('nombre')

    # Verifica si el usuario ya existe
    if _usuario_existe(username):
        mensaje_error = 'Usuario ya existe'
        registrar_log(f"Usuario '{username}' no pudo completar el registro correctamente: {mensaje_error}.")
        return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400

    _agregar_usuario(username, clave, nombre)

    usuarios = _obtener_usuarios()
    usuario = next(usuario for usuario in usuarios if usuario["usuario"] == username)

    return jsonify({'mensaje': 'Usuario registrado exitosamente', 'usuario': usuario}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('usuario')
    password = request.json.get('clave')

    usuarios = _obtener_usuarios()

    # Verifica si el usuario existe
    if not any(usuario["usuario"] == username for usuario in usuarios):
        mensaje_error = 'Nombre de usuario no encontrado'
        registrar_log(f"Usuario '{username}' no pudo iniciar sesión correctamente: {mensaje_error}.")
        return jsonify({'error': 'Nombre de usuario no encontrado'}), 401

    # Verifica la contraseña
    usuario = next(usuario for usuario in usuarios if usuario["usuario"] == username)
    if usuario["clave"] == password:
        registrar_log(f"Usuario '{username}' ha iniciado sesión correctamente.")
        return jsonify({'mensaje': 'Inicio de sesión exitoso', "usuario": usuario}), 200
    else:
        mensaje_error = 'Contraseña incorrecta'
        registrar_log(f"Usuario '{username}' no pudo iniciar sesión correctamente: {mensaje_error}.")
        return jsonify({'error': mensaje_error}), 401

def _usuario_existe(username):
    usuarios = _obtener_usuarios()
    return any(usuario["usuario"] == username for usuario in usuarios)

def _agregar_usuario(username, clave, nombre):
    # Agrega el nuevo usuario al archivo JSON
    usuarios = _obtener_usuarios()
    nuevo_usuario = {
        "usuario":username,
        "clave": clave,
        "nombre": nombre
    }
    usuarios.append(nuevo_usuario)
    registrar_log(f"Usuario '{username}' se ha registrado correctamente.")
    _guardar_usuarios(usuarios)

def _obtener_usuarios():
    try:
        with open('config/usuarios.json', 'r') as file:
            usuarios = json.load(file)
    except FileNotFoundError:
        usuarios = []
    return usuarios

def _guardar_usuarios(usuarios):
    with open('config/usuarios.json', 'w') as file:
        json.dump(usuarios, file, indent=4)

def registrar_log(mensaje, contenido=""):
    # Registra un log con la fecha y hora actual en el archivo logs.txt
    fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = f"[{fecha_hora_actual}] {mensaje}\n"

    with open('logs/actividad.log', 'a', encoding='utf-8') as archivo_logs:
        archivo_logs.write(log)
        if contenido != "":
            archivo_logs.write(f"{contenido}\n")


if __name__ == '__main__':
    app.run(debug=True)