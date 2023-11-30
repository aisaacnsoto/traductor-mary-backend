import datetime, os

class LogUtil:
    
    def _registrar_log(self, mensaje, contenido=""):
        fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = f"[{fecha_hora_actual}] {mensaje}\n"
        with open(os.path.join(os.getcwd(), 'logs/actividad.log'), 'a', encoding='utf-8') as archivo_logs:
            archivo_logs.write(log)
            if contenido != "":
                archivo_logs.write(f"{contenido}\n")

    def registrar_log_login_fallido(self, username, mensaje_error):
        mensaje_log = f"Usuario '{username}' no pudo iniciar sesión correctamente: {mensaje_error}."
        self._registrar_log(mensaje_log)

    def registrar_log_login_exitoso(self, username):
        self._registrar_log(f"Usuario '{username}' ha iniciado sesión correctamente.")

    def registrar_log_registro_exitoso(self, username):
        self._registrar_log(f"Usuario '{username}' se ha registrado correctamente.")

    def registrar_log_username_repetido(self, username, mensaje_error):
        self._registrar_log(f"Usuario '{username}' no pudo completar el registro correctamente: {mensaje_error}.")
                        
    def registrar_log_traduccion(self, username, text, translation, to_lang, audio_path):
        mensaje_log = f"Usuario '{username}' ha realizado una traducción."
        contenido_log = f"Texto: {text}\nTraducción: {translation}\nIdioma: {to_lang}\nAudio: {audio_path}"
        self._registrar_log(mensaje_log, contenido_log)

    def registrar_log_imagen_subida(self, username, texto_reconocido, ruta_imagen):
        mensaje_log = f"Usuario '{username}' ha cargado una foto."
        contenido_log = f"Texto reconocido: {texto_reconocido}\nFoto: {ruta_imagen}"
        self._registrar_log(mensaje_log, contenido_log)
                        