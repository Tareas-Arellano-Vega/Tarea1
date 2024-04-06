import json
import os
import random
import string
import hashlib
from getpass import getpass

PASSWORD_FILE = "contrasenas.json"


#inicio menu
class Menu_contra:
    def __init__(self):
        self.contrasena = {}
        self.cargar_contrasena()
    
    #funcion para obtener las contraseñas guardadas json
    def cargar_contrasena(self):
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, "r") as file:
                self.contrasena = json.load(file)
    #funcion para guardar contraseñas en el json
    def guardar_contrasena(self):
        with open(PASSWORD_FILE, "w") as file:
            json.dump(self.contrasena, file, indent=4)

    #funcion que realiza un hashing a las contraseñas
    def hashing(self, contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()
    
    #Funcion que permite añadir ontraseñas al usuario (solicita web, usuario, contraseña y palabra clave)
    def anadir_contrasena(self):
        web = input("Web a la que pertece la contraseña: ")
        nombre_usuario = input("Nombre de Usuario: ")
        palabra_clave = input("Palabra clave: ")
        contrasena = getpass("Contraseña: ")
        self.contrasena[self.hashing(web)] = {"nombre_usuario": nombre_usuario , "contrasena": contrasena, "palabra_clave": palabra_clave}
        self.guardar_contrasena()
        print("Contraseña guardada correctamente.")

    #Funcion que permite obtener y visualizar contraseñas al usuario (solicita web, usuario, contraseña y palabra clave)
    def obtener_contrasena(self):
        web = input("Web de la contraseña a solicitar: ")
        hashed_web = self.hashing(web)
        if hashed_web in self.contrasena:
            data = self.contrasena[hashed_web]
            print("Nombre de Usuario: ", data["nombre_usuario"])
            print("Contraseña: ", data["contrasena"])
            print("Palabra Clave: ", data.get("palabra_clave", "N/A"))
        else:
            print("Contraseña no encontrada.")
    #Funcion que permite actualizar la infomacion de las  contraseñas  guardadas por el usuario (solicita web, usuario, contraseña y palabra clave)
    def actualizar_contrasena(self):
        web = input("Web a la que pertece la contraseña: ")
        hashed_web = self.hashing(web)
        if hashed_web in self.contrasena:
            print("Ingresa los nuevos datos (dejar en blanco si no se quiere cambiar)")
            new_nombre_usuario = input("Nuevo Usuario: ")
            new_palabra_clave = input("Nueva Palabra Clave: ")
            new_contrasena = getpass("Nueva Contraseña: ")
            data = self.contrasena[hashed_web]
            data["nombre_usuario"] = new_nombre_usuario or data["nombre_usuario"]
            data["contrasena"] = new_contrasena or data["contrasena"]
            data["palabra_clave"] =  new_palabra_clave or data["palabra_clave"]
            self.contrasena[hashed_web] = data
            self.guardar_contrasena()
            print("Contraseña actualizada con exito.")
        else:
            print("Contraseña no encontrada.")

    #Funcion que permite borrar contraseñas al usuario (solicita web)
    def borrar_contrasena(self):
        web = input("Web a la que pertenece la contraseña: ")
        hashed_web = self.hashing(web)
        if hashed_web in self.contrasena:
            del self.contrasena[hashed_web]
            self.guardar_contrasena()
            print("Contraseña borrada exitosamente.")
        else:
            print("Contraseña no encontrada.")
    #Funcion que permite generar contraseñas al usuario 
    def generador_contrasena(self, length=12, chars=string.ascii_letters + string.digits + string.punctuation):
        return ''.join(random.choice(chars) for _ in range(length))
    

if __name__ == "__main__":
    menu_contra = Menu_contra()
    #Menu principal
    while True:
        print("\n1. Añadir contraseña")
        print("2. Obtener contraseña")
        print("3. Actualizar contraseña")
        print("4. Borrar contraseña")
        print("5. Generar contraseña")
        print("6. Salir")
        

        eleccion = input("Ingresa el número de la acción que deseas realizar: ")

        if eleccion == "1":
            menu_contra.anadir_contrasena()
        elif eleccion == "2":
            menu_contra.obtener_contrasena()
        elif eleccion == "3":
            menu_contra.actualizar_contrasena()
        elif eleccion == "4":
            menu_contra.borrar_contrasena()
        elif eleccion == "5":
            length = int(input("Ingresa la longitud que desea la contraseña: "))
            #allowed_chars = input("Ingresa los caracteres que deseas en tu contraseña (presiona enter para caracteres determinados): ") or string.ascii_letters + string.digits + string.punctuation
            print("Contraseña generada: ", menu_contra.generador_contrasena(length)) # Para utilizar la opcion anterior debe escribir , allowed_chars dentro de esta funcion
        elif eleccion == "6":
            break
        else:
            print("Opción invalida. Por favor intentalo denuevo.")
        
        



    


