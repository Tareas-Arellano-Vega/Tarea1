import json
import os
import random
import string
import hashlib
from getpass import getpass
from cryptography.fernet import Fernet

#creacion de carpeta de perfiles y archivo de la llave secreta
PROFILE_FOLDER = "profiles"
SECRET_KEY_FILE = "secret.key"

#Clase que contiene la funciones relacionadas con los perfiles
class ProfileManager:
    def __init__(self):
        self.active_profile = None
    #funcion que permite la creacion del perfil, tanto el nombre como la contraseña que se encripta
    def create_profile(self, profile_name, password):
        profile_folder = os.path.join(PROFILE_FOLDER, profile_name)
        if os.path.exists(profile_folder):
            print("El perfil ya existe. Por favor, elige otro nombre.")
            return
        os.makedirs(profile_folder, exist_ok=True)
        password_file = os.path.join(profile_folder, "password.txt")
        with open(password_file, "wb") as file:
            f = Fernet(self.load_secret_key())
            encrypted_password = f.encrypt(password.encode())
            file.write(encrypted_password)
    #funcion que permite seleccionar el perfil para asi poder administrar las contrasenas del perfil seleccionado, se requiere de la contrasena del perfil a seleccionar
    def select_profile(self, profile_name, password):
        profile_folder = os.path.join(PROFILE_FOLDER, profile_name)
        password_file = os.path.join(profile_folder, "password.txt")
        if os.path.exists(profile_folder) and os.path.exists(password_file):
            with open(password_file, "rb") as file:
                encrypted_password = file.read()
                f = Fernet(self.load_secret_key())
                decrypted_password = f.decrypt(encrypted_password).decode()
                if decrypted_password == password:
                    self.active_profile = profile_name
                    return True
                else:
                    print("Contraseña incorrecta.")
                    return False
        else:
            print("Perfil no encontrado.")
            return False
    #Funcion que permite borrar perfiles, se requieren las contraseñas de estos ultimos para poder efectuar esta funcion
    def delete_profile(self, profile_name, password):
        profile_folder = os.path.join(PROFILE_FOLDER, profile_name)
        if os.path.exists(profile_folder):
            # Limpiar el contenido del directorio antes de intentar eliminarlo
            for file_name in os.listdir(profile_folder):
                file_path = os.path.join(profile_folder, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            # Una vez que el directorio esté vacío, se puede eliminar
            try:
                os.rmdir(profile_folder)
                print("Profile deleted successfully.")
            except OSError as e:
                print(f"Failed to delete profile directory: {e}")
        else:
            print("Profile does not exist.")
    #funcion que carga la secret key para las contraseñas encriptadas de los perfiles
    def load_secret_key(self):
        if not os.path.exists(SECRET_KEY_FILE):
            with open(SECRET_KEY_FILE, "wb") as file:
                file.write(Fernet.generate_key())
        with open(SECRET_KEY_FILE, "rb") as file:
            return file.read()
        
#Clase donde estan toda la logica y funciones para la administracion de contraseñas
class MenuContra:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.active_profile = None
        self.contrasena = {}
        self.secret_key = None

    #funcion que carga la secret key para la encriptacion y desencriptacion de las contraseñas guardadas
    def load_secret_key(self):
        if not os.path.exists(SECRET_KEY_FILE):
            with open(SECRET_KEY_FILE, "wb") as file:
                file.write(Fernet.generate_key())
        with open(SECRET_KEY_FILE, "rb") as file:
            return file.read()
        
    #funcion que permite cargar las contraseñas encriptadas
    def load_passwords(self):
        if self.active_profile is not None:
            profile_folder = os.path.join(PROFILE_FOLDER, self.active_profile)
            password_file = os.path.join(profile_folder, "contrasenas.json")
            if os.path.exists(password_file):
                with open(password_file, "rb") as file:
                    encrypted_data = file.read()
                    decrypted_data = self.desencriptar_data(encrypted_data)
                    if decrypted_data:
                        self.contrasena = json.loads(decrypted_data.decode())
            else:
                # Si el archivo no existe, inicializamos self.contrasena como un diccionario vacío
                self.contrasena = {}

    #Funcion que permite desencriptar la data del perfil seleccionado
    def desencriptar_data(self, encrypted_data):
        f = Fernet(self.load_secret_key())
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data
    
    #funcion que realiza la logica del guardado de las contraseñas encriptadas
    def save_passwords(self):
        if self.active_profile is not None:
            profile_folder = os.path.join(PROFILE_FOLDER, self.active_profile)
            password_file = os.path.join(profile_folder, "contrasenas.json")
            with open(password_file, "wb") as file:
                f = Fernet(self.load_secret_key())
                encrypted_data = f.encrypt(json.dumps(self.contrasena).encode())
                file.write(encrypted_data)

    #Funcion que realiza el hashing MD5 
    def hashing(self, contrasena):
        return hashlib.md5(contrasena.encode()).hexdigest()
    
    #funcion que realiza la logica de añadir las contraseñas con sus respectivos datos
    def anadir_contrasena(self):
        web = input("Web a la que pertenece la contraseña: ")
        nombre_usuario = input("Nombre de Usuario: ")
        palabra_clave = input("Palabra clave: ")
        contrasena = getpass("Contraseña: ")
        self.load_passwords()
        self.contrasena[self.hashing(web)] = {
            "nombre_usuario": nombre_usuario,
            "contrasena": self.encriptar_contrasena(contrasena),
            "palabra_clave": palabra_clave
        }
        self.save_passwords()
        print("Contraseña guardada correctamente.")

    #funcion que obtienen los datos de la contraseña para mostrarlo por pantalla (se solicita el nombre de la web de la contraseña para realizar esta funcion)
    def obtener_contrasena(self):
        web = input("Web de la contraseña a solicitar: ")
        hashed_web = self.hashing(web)
        self.load_passwords()
        if hashed_web in self.contrasena:
            data = self.contrasena[hashed_web]
            print("Nombre de Usuario: ", data["nombre_usuario"])
            decrypted_password = self.desencriptar_contrasena(data["contrasena"])
            print("Contraseña: ", decrypted_password)
            print("Palabra Clave: ", data.get("palabra_clave", "N/A"))
        else:
            print("Contraseña no encontrada.")

    #funcion que realiza la logica de encriptacion contraseñas
    def encriptar_contrasena(self, password):
        f = Fernet(self.load_secret_key())
        encrypted_password = f.encrypt(password.encode()).decode()
        return encrypted_password

    #funcion que reliza la logica de desencriptacion de contraseñas
    def desencriptar_contrasena(self, encrypted_password):
        f = Fernet(self.load_secret_key())
        decrypted_password = f.decrypt(encrypted_password.encode()).decode()
        return decrypted_password

    #funcion que permite actualizar los datos de una contraseña guardada por el usuario(perfil)(se solicita el nombre de la web de la contraseña para realizar esta funcion)
    def actualizar_contrasena(self):
        web = input("Web a la que pertenece la contraseña: ")
        hashed_web = self.hashing(web)
        self.load_passwords()
        if hashed_web in self.contrasena:
            print("Ingresa los nuevos datos (dejar en blanco si no se quiere cambiar)")
            new_nombre_usuario = input("Nuevo Usuario: ")
            new_palabra_clave = input("Nueva Palabra Clave: ")
            new_contrasena = getpass("Nueva Contraseña: ")
            data = self.contrasena[hashed_web]
            data["nombre_usuario"] = new_nombre_usuario or data["nombre_usuario"]
            data["contrasena"] = self.encriptar_contrasena(new_contrasena) if new_contrasena else data["contrasena"]
            data["palabra_clave"] = new_palabra_clave or data["palabra_clave"]
            self.contrasena[hashed_web] = data
            self.save_passwords()
            print("Contraseña actualizada con éxito.")
        else:
            print("Contraseña no encontrada.")

    #funcion que permite borrar contraseñas guardadas (se solicita el nombre de la web de la contraseña para realizar esta funcion)
    def borrar_contrasena(self):
        web = input("Web a la que pertenece la contraseña: ")
        hashed_web = self.hashing(web)
        self.load_passwords()
        if hashed_web in self.contrasena:
            del self.contrasena[hashed_web]
            self.save_passwords()
            print("Contraseña borrada exitosamente.")
        else:
            print("Contraseña no encontrada.")

    #funcion que permite generar una contraseña con ciertos criterios, el usuario elige el largo
    def generador_contrasena(self, length=12, chars=string.ascii_letters + string.digits + string.punctuation):
        return ''.join(random.choice(chars) for _ in range(length))

    #Funcion del menu que se muestra al usuario
    def run(self):
        while True:
            print("\n1. Crear perfil")
            print("2. Seleccionar perfil")
            print("3. Eliminar perfil")
            print("4. Administrar contraseñas")
            print("5. Salir")

            choice = input("Ingresa el número de la acción que deseas realizar: ")

            if choice == "1":
                profile_name = input("Nombre del perfil: ")
                profile_password = getpass("Contraseña del perfil: ")
                self.profile_manager.create_profile(profile_name, profile_password)
            elif choice == "2":
                profile_name = input("Nombre del perfil: ")
                profile_password = getpass("Contraseña del perfil: ")
                if self.profile_manager.select_profile(profile_name, profile_password):
                    print(f"Perfil '{profile_name}' seleccionado.")
                    self.active_profile = profile_name
                    self.load_passwords()
            elif choice == "3":
                profile_name = input("Nombre del perfil a eliminar: ")
                profile_password = getpass("Contraseña del perfil: ")
                self.profile_manager.delete_profile(profile_name, profile_password)
            elif choice == "4":
                if self.active_profile is None:
                    print("Por favor selecciona un perfil primero.")
                else:
                    profile_password = getpass("Contraseña del perfil: ")
                    if self.profile_manager.select_profile(self.active_profile, profile_password):
                        while True:
                            print("\n--- Administrar Contraseñas ---")
                            print("1. Añadir Contraseña")
                            print("2. Obtener Contraseña")
                            print("3. Actualizar Contraseña")
                            print("4. Borrar Contraseña")
                            print("5. Generar Contraseña")
                            print("6. Volver al menú principal")

                            sub_choice = input("Ingresa el número de la acción que deseas realizar: ")

                            if sub_choice == "1":
                                self.anadir_contrasena()
                            elif sub_choice == "2":
                                self.obtener_contrasena()
                            elif sub_choice == "3":
                                self.actualizar_contrasena()
                            elif sub_choice == "4":
                                self.borrar_contrasena()
                            elif sub_choice == "5":
                                length = int(input("Ingresa la longitud de la contraseña: "))
                                print("Contraseña generada: ", self.generador_contrasena(length))
                            elif sub_choice == "6":
                                break
                            else:
                                print("Opción inválida. Por favor intenta de nuevo.")
            elif choice == "5":
                break
            else:
                print("Opción inválida. Por favor intenta de nuevo.")

#main
if __name__ == "__main__":
    menu_contra = MenuContra()
    menu_contra.run()
        
        



    


