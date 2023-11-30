import json, os

class UserUtil:

    def __init__(self):
        self.ruta_usuarios = os.path.join(os.getcwd(), 'config/usuarios.json')
        self.usuarios = self._obtener_usuarios()

    def verificar_username(self, username):
        if not self._usuario_existe(username):
            return True
        else:
            return False
        
    def verificar_password(self, username, password):
        usuario = self._obtener_usuario(username)
        if usuario["clave"] == password:
            return usuario
        else:
            return False
    
    def registrar_usuario(self, username, clave, nombre):
        
        self._agregar_usuario(username, clave, nombre)
        
        usuario = self._obtener_usuario(username)

        return usuario
        
    def _usuario_existe(self, username):
        return any(usuario["usuario"] == username for usuario in self.usuarios)

    def _agregar_usuario(self, username, clave, nombre):
        nuevo_usuario = {
            "usuario":username,
            "clave": clave,
            "nombre": nombre
        }
        self.usuarios.append(nuevo_usuario)
        self._guardar_usuarios()

    def _obtener_usuario(self, username):
        return next(usuario for usuario in self.usuarios if usuario["usuario"] == username)
    
    def _obtener_usuarios(self):
        try:
            with open(self.ruta_usuarios, 'r') as file:
                usuarios = json.load(file)
        except FileNotFoundError:
            usuarios = []
        return usuarios

    def _guardar_usuarios(self):
        with open(self.ruta_usuarios, 'w') as file:
            json.dump(self.usuarios, file, indent=4)
