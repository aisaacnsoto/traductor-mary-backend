
from flask import Flask, request, jsonify, send_file # pip install flask
from flask_cors import CORS # pip install flask_cors

from utils.log_util import LogUtil
from utils.traductor_util import TraductorUtil
from utils.user_util import UserUtil

class TraductorMary(LogUtil, TraductorUtil, UserUtil):

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.configurar_rutas()
        UserUtil.__init__(self)
        TraductorUtil.__init__(self)

    def configurar_rutas(self):
        self.app.route('/cargar_imagen', methods=['POST'])(self.cargar_imagen)
        self.app.route('/traducir', methods=['POST'])(self.traducir)
        self.app.route('/registro', methods=['POST'])(self.registro)
        self.app.route('/login', methods=['POST'])(self.login)

    def cargar_imagen(self):
        try:
            imagen_base64 = request.json.get('imagen')
            usuario = request.json.get('usuario')
        
            if imagen_base64:
                ruta_imagen = self.guardar_imagen(imagen_base64)
                texto_reconocido = self.reconocer_texto(ruta_imagen)
                self.registrar_log_imagen_subida(usuario, texto_reconocido, ruta_imagen)
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
        
    
    def traducir(self):
        try:
            text = request.json.get('texto')
            to_lang = request.json.get('idioma')
            usuario = request.json.get('usuario')

            if (text):
                translation = self.traducir_texto(text, to_lang)
                audio_path = self.guardar_audio(translation, to_lang)
                self.registrar_log_traduccion(usuario, text, translation, to_lang, audio_path)
                return send_file(audio_path, mimetype='audio/mp3')
            else:
                return jsonify({"error": "No se ha encontrado nada para traducir"})

        except Exception as e:
                print('se ha producido una excepción: '+e.__str__())
                return jsonify({"mensaje": "intenta otra vez"})

    def registro(self):
        username = request.json.get('usuario')
        clave = request.json.get('clave')
        nombre = request.json.get('nombre')

        if self._usuario_existe(username):
            mensaje_error = 'El nombre de usuario ya está en uso'
            self.registrar_log_username_repetido(username, mensaje_error)
            return jsonify({'error': mensaje_error}), 400

        usuario_registrado = self.registrar_usuario(username, clave, nombre)
        if (usuario_registrado):
            self.registrar_log_registro_exitoso(username)
            return jsonify({'mensaje': 'Usuario registrado exitosamente', 'usuario': usuario_registrado}), 201


    def login(self):
        username = request.json.get('usuario')
        password = request.json.get('clave')

        if self.verificar_username(username):
            mensaje_error = 'Nombre de usuario no encontrado'
            self.registrar_log_login_fallido(username, mensaje_error)
            return jsonify({'error': mensaje_error}), 401

        usuario_autenticado = self.verificar_password(username, password)
        if usuario_autenticado:
            mensaje = 'Inicio de sesión exitoso'
            self.registrar_log_login_exitoso(username)
            return jsonify({'mensaje': mensaje, "usuario": usuario_autenticado}), 200
        else:
            mensaje_error = 'Contraseña incorrecta'
            self.registrar_log_login_fallido(username, mensaje_error)
            return jsonify({'error': mensaje_error}), 401

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = TraductorMary()
    app.run()