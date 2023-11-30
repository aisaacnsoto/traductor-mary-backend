
from flask import Flask, request, jsonify, send_file # pip install flask
from flask_cors import CORS # pip install flask_cors

from utils.log_util import LogUtil
from utils.traductor_util import TraductorUtil
from utils.user_util import UserUtil

log_util = LogUtil()
traductor_util = TraductorUtil()
user_util = UserUtil()

app = Flask(__name__)
CORS(app)

@app.route('/cargar_imagen', methods=['POST'])
def cargar_imagen():
    try:
        imagen_base64 = request.json.get('imagen')
        usuario = request.json.get('usuario')
    
        if imagen_base64:
            ruta_imagen = traductor_util.guardar_imagen(imagen_base64)
            texto_reconocido = traductor_util.reconocer_texto(ruta_imagen)
            log_util.registrar_log_imagen_subida(usuario, texto_reconocido, ruta_imagen)
            return jsonify({
                "texto_reconocido": texto_reconocido,
                "mensaje": "Imagen cargada correctamente",
                "nombre_archivo": ruta_imagen
                })
        else:
            return jsonify({"mensaje": "No se proporcionó ninguna imagen en la solicitud"}), 400
    except Exception as e:
        print('se ha producido una excepción: '+e)
        return jsonify({"mensaje": "intenta otra vez"})

# Ruta para reconocer texto de una imagen
@app.route('/traducir', methods=['POST'])
def traducir():
    
    try:
        text = request.json.get('texto')
        to_lang = request.json.get('idioma')
        usuario = request.json.get('usuario')

        if (text):
            translation = traductor_util.traducir_texto(text, to_lang)
            audio_path = traductor_util.guardar_audio(translation, to_lang)
            log_util.registrar_log_traduccion(usuario, text, translation, to_lang, audio_path)
            return send_file(audio_path, mimetype='audio/mp3')
        else:
            return jsonify({"error": "No se ha encontrado nada para traducir"})

    except Exception as e:
            print('se ha producido una excepción: '+e.__str__())
            return jsonify({"mensaje": "intenta otra vez"})

@app.route('/registro', methods=['POST'])
def registro():
    username = request.json.get('usuario')
    clave = request.json.get('clave')
    nombre = request.json.get('nombre')

    if user_util._usuario_existe(username):
        mensaje_error = 'El nombre de usuario ya está en uso'
        log_util.registrar_log_username_repetido(username, mensaje_error)
        return jsonify({'error': mensaje_error}), 400

    usuario_registrado = user_util.registrar_usuario(username, clave, nombre)
    if (usuario_registrado):
        log_util.registrar_log_registro_exitoso(username)
        return jsonify({'mensaje': 'Usuario registrado exitosamente', 'usuario': usuario_registrado}), 201


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('usuario')
    password = request.json.get('clave')

    if user_util.verificar_username(username):
        mensaje_error = 'Nombre de usuario no encontrado'
        log_util.registrar_log_login_fallido(username, mensaje_error)
        return jsonify({'error': mensaje_error}), 401

    usuario_autenticado = user_util.verificar_password(username, password)
    if usuario_autenticado:
        mensaje = 'Inicio de sesión exitoso'
        log_util.registrar_log_login_exitoso(username)
        return jsonify({'mensaje': mensaje, "usuario": usuario_autenticado}), 200
    else:
        mensaje_error = 'Contraseña incorrecta'
        log_util.registrar_log_login_fallido(username, mensaje_error)
        return jsonify({'error': mensaje_error}), 401

if __name__ == '__main__':
    app.run(debug=True)