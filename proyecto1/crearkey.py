import os

# Generar una cadena de 24 bytes aleatoria y segura
secret_key = os.urandom(24)
print(secret_key)  # Esta es tu SECRET_KEY
# Convertir la cadena de bytes a formato hexadecimal
secret_key_hex = secret_key.hex()
print(secret_key_hex)  # Convertida a cadena hexadecimal
