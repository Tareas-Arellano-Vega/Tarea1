from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import pymongo
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


#Configuracion Flask-Mail
app = Flask(__name__)
CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP de Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pabloarellano107@gmail.com'  # Tu correo electrónico
app.config['MAIL_PASSWORD'] = 'ruow cjfx ssmy dgzf'  # Tu contraseña
mail = Mail(app)

#cargar variables de entorno
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_fallback_key') 


#Configuracion Mongo

mongo_uri = "mongodb://localhost:27017"
client = pymongo.MongoClient(mongo_uri)


#Seleccionar la base de datos y coleccion

db = client.Proyecto1
collection = db.Medicos

collecionadmin = db.Admin

collection_data= db.Citas

#funcion enviar correo
def enviar_confirmacion(email, cita_id):
    msg = Message(
        "Confirmación de Cita Médica",
        sender=app.config['MAIL_USERNAME'],  # Cambia por el correo del remitente
        recipients=[email]  # Correo del paciente
    )
    msg.body = f"Su cita ha sido confirmada. El ID de la cita es {cita_id}."
    mail.send(msg)


#Ruta citas

@app.route('/citas', methods=['POST'])
def programar_cita():
    cita_data = request.get_json()

    # Validar campos requeridos
    required_fields = ["paciente", "especialista_id", "fecha", "hora", "correo_paciente"]
    missing_fields = [field for field in required_fields if field not in cita_data]

    if missing_fields:
        return jsonify({"message": "Faltan campos requeridos", "missing": missing_fields}), 400

    especialista_id = cita_data["especialista_id"]
    fecha = cita_data["fecha"]
    hora = cita_data["hora"]

    # Verificar conflictos de horarios para el especialista
    conflicto = collection_data.find_one({
        "especialista_id": especialista_id,
        "fecha": fecha,
        "hora": hora
    })

    if conflicto:
        return jsonify({"message": "El especialista ya tiene una cita en ese horario"}), 409

    # Insertar la nueva cita
    result = collection_data.insert_one(cita_data)

    # Enviar confirmación por correo electrónico
    email = cita_data["correo_paciente"]
    if email:
        enviar_confirmacion(email, str(result.inserted_id))

    return jsonify({"message": "Cita programada", "id": str(result.inserted_id)}), 201


@app.route('/citas/<id>', methods=['DELETE'])
def delete_cita_by_id(id):
    # Intentar eliminar la cita por ID
    result = collection_data.delete_one({"_id": ObjectId(id)})

    # Verificar si la cita fue eliminada
    if result.deleted_count > 0:
        return jsonify({"message": "Cita eliminada"}), 200
    else:
        return jsonify({"message": "Cita no encontrada"}), 404

#Rutas credenciales de admins
#ruta registrar admin
@app.route('/register_admin', methods=['POST'])
def register_admin():
    admin_data = request.get_json()

    # Verificar campos requeridos
    required_fields = ["name", "email", "password"]
    missing_fields = [field for field in required_fields if field not in admin_data]

    if missing_fields:
        return jsonify({"message": "Faltan campos requeridos", "missing": missing_fields}), 400

    # Verificar si el email ya está en uso
    existing_admin = collecionadmin.find_one({"email": admin_data["email"]})
    if existing_admin:
        return jsonify({"message": "Email ya registrado"}), 400

    # Hashear la contraseña con un método compatible
    hashed_password = generate_password_hash(admin_data["password"], method='pbkdf2:sha256')

    # Insertar el nuevo administrador en la colección
    admin_data["password"] = hashed_password
    result = collecionadmin.insert_one(admin_data)

    return jsonify({"message": "Administrador registrado", "id": str(result.inserted_id)}), 201



#ruta Verificar logins
@app.route('/login', methods=['POST'])
def login():
    auth_data = request.get_json()

    # Verificar campos requeridos
    required_fields = ["email", "password"]
    missing_fields = [field for field in required_fields if field not in auth_data]

    if missing_fields:
        return jsonify({"message": "Faltan campos requeridos", "missing": missing_fields}), 400

    # Buscar el administrador por email
    admin = collecionadmin.find_one({"email": auth_data["email"]})

    if not admin or not check_password_hash(admin["password"], auth_data["password"]):
        return jsonify({"message": "Credenciales incorrectas"}), 401

    # Generar un token JWT
    token = jwt.encode(
        {
            "admin_id": str(admin["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Expira en 24 horas
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"message": "Autenticación exitosa", "token": token})

#ruta para proteger endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"message": "Token de autenticación requerido"}), 401

        try:
            token = token.split(" ")[1]  # Eliminar el prefijo "Bearer"
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_admin = collecionadmin.find_one({"_id": ObjectId(data["admin_id"])})
        except:
            return jsonify({"message": "Token inválido o expirado"}), 401

        return f(current_admin, *args, **kwargs)

    return decorated




# Ruta obtener todos los medicos o filtrar respecto a nombre completo, especialidad , ciudad o pais(quizas cambiar por region)
@app.route('/medicos/filter', methods=['GET'])
def filter_medicos():
    query = {}

    # Filtrar por nombre completo
    nombre_completo = request.args.get("nombre_completo")
    if nombre_completo:
        # Buscamos por nombre completo
        query["nombre_completo"] = {"$regex": nombre_completo, "$options": "i"}

    # Filtrar por especialización
    especializacion = request.args.get("especializacion")
    if especializacion:
        query["especializacion"] = {"$regex": especializacion, "$options": "i"}

    # Filtrar por ciudad, estado, o país
    ciudad = request.args.get("ciudad")
    if ciudad:
        query["ciudad"] = {"$regex": ciudad, "$options": "i"}


    region = request.args.get("region")
    if region:
        query["region"] = {"$regex": region, "$options": "i"}

    # Obtener los médicos que coincidan con la consulta
    medicos = list(collection.find(query))

    # Convertir ObjectId a cadenas para enviar como JSON
    for medico in medicos:
        medico["_id"] = str(medico["_id"])

    return jsonify(medicos)



### RUTAS GESTION DE MEDICOS ###

# Ruta para crear un nuevo médico
@app.route('/medicos', methods=['POST'])
#@token_required
def create_medico():
    # Obtener los datos del cuerpo de la solicitud
    medico_data = request.get_json()

    # Validar que los campos esenciales estén presentes
    required_fields = ["nombre", "apellido", "rut", "especializacion", "ciudad", "region", "direccion"]
    missing_fields = [field for field in required_fields if field not in medico_data]

    if missing_fields:
        return jsonify({"message": "Faltan campos requeridos", "missing": missing_fields}), 400
    

    # Crear campo de nombre completo
    medico_data["nombre_completo"] = f"{medico_data['nombre']} {medico_data['apellido']}"

    # Insertar el nuevo médico en la colección
    result = collection.insert_one(medico_data)

    return jsonify({"message": "Médico creado", "id": str(result.inserted_id)}), 201


# Ruta para obtener un médico por ID
@app.route('/medicos/<id>', methods=['GET'])
#@token_required
def get_medico_by_id(id):
    medico = collection.find_one({"_id": ObjectId(id)})
    if medico:
        medico["_id"] = str(medico["_id"])
        return jsonify(medico)
    else:
        return jsonify({"message": "Médico no encontrado"}), 404
    

# Ruta para actualizar un médico por ID
@app.route('/medicos/<id>', methods=['PUT'])
#@token_required
def update_medico_by_id(id):
    update_data = request.get_json()

    # Si el nombre o el apellido cambian, actualiza el campo nombre_completo
    nombre = update_data.get("nombre")
    apellido = update_data.get("apellido")

    if nombre or apellido:
        # Busca el médico actual para obtener sus datos existentes
        medico_actual = collection.find_one({"_id": ObjectId(id)})

        if not medico_actual:
            return jsonify({"message": "Médico no encontrado"}), 404

        # Si se cambió el nombre o el apellido, reconstruir el nombre completo
        nuevo_nombre = nombre if nombre else medico_actual["nombre"]
        nuevo_apellido = apellido if apellido else medico_actual["apellido"]
        update_data["nombre_completo"] = f"{nuevo_nombre} {nuevo_apellido}"

    # Actualizar el médico con los datos proporcionados
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    if result.matched_count:
        return jsonify({"message": "Médico actualizado"})
    else:
        return jsonify({"message": "Médico no encontrado"}), 404




# Ruta para eliminar un médico por ID
@app.route('/medicos/<id>', methods=['DELETE'])
#@token_required
def delete_medico_by_id(id):
    result = collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count:
        return jsonify({"message": "Médico eliminado"})
    else:
        return jsonify({"message": "Médico no encontrado"}), 404




if __name__ == '__main__':
    app.run(port=3001,debug=True)


