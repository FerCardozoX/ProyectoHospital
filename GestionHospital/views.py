from datetime import datetime, time
import json
from multiprocessing import context
from bson import ObjectId
import certifi
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password,check_password
from .models import *
from pymongo import MongoClient



@csrf_exempt
@api_view(['POST'])
def login(request):
    usuario = request.data.get('usuario')
    contraseña = request.data.get('contraseña')
    
    try:
        user = Usuario.objects.get(usuario=usuario)
    except Usuario.DoesNotExist:
        user = None
    
    if user is not None and check_password(contraseña, user.contraseña):
        rol = Rol.objects.get(idRol=user.idRol_id)
        
        response_data = {
            'nombre': user.usuario,
            'rol': {
                'idRol': user.idRol_id,
                'rol': rol.rol
            }
        }
        return JsonResponse(response_data, status=202)
    else:
        response_data = {
            'error': 'Usuario o Contraseña Incorrecto'
        }
        return JsonResponse(response_data, status=400)
 
#GetAll

@csrf_exempt
@api_view(['GET'])
def getPacientes(request):
    pacientes = Paciente.objects.all().values()
    return JsonResponse(list(pacientes), status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getMedicos(request):
    Medicos = Medico.objects.all().values()
    return JsonResponse(list(Medicos), status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getCitas(request):
    Citas = Cita.objects.all().values()
    return JsonResponse(list(Citas), status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getAdministrativos(request):
    Administrativos = Administrativo.objects.all().values()
    return JsonResponse(list(Administrativos), status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getUsuarios(request):
    Usuarios = Usuario.objects.all().values()
    return JsonResponse(list(Usuarios), status=200, safe=False)

#CrearPaciente

@csrf_exempt
@api_view(['POST'])
def postCrearPaciente(request):
    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')
    dni = request.data.get('dni')
    email = request.data.get('email')
    fecha_nacimiento = request.data.get('fecha_nacimiento')
    genero = request.data.get('genero')
    telefono = request.data.get('telefono')
    contacto_emergencia = request.data.get('contacto_emergencia')

    if not all([nombre, apellido, dni, email, fecha_nacimiento, genero, telefono, contacto_emergencia]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    if Paciente.objects.filter(dni=dni).exists():
        return JsonResponse({"error": "El Paciente ya existe"}, status=400)

    paciente = Paciente(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        email=email,
        fecha_nacimiento=fecha_nacimiento,
        genero=genero,
        telefono=telefono,
        contacto_emergencia=contacto_emergencia
    )
    paciente.save()

    success, result = agregar_historial_medico_vacio(paciente.idPaciente)
    if not success:
        raise Exception(result)

    return JsonResponse({"message": "Paciente Creado con Éxito", "historial_id": result}, status=201)
    

#Crear médico con su usuario

@csrf_exempt
@api_view(['POST'])
def registrar_Medico(request):
    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')
    dni = request.data.get('dni')
    email = request.data.get('email')
    genero = request.data.get('genero')
    fecha_nacimiento = request.data.get('fecha_nacimiento')
    telefono = request.data.get('telefono')
    especialidad = request.data.get('especialidad')
    matricula = request.data.get('matricula')

    print('La info llegó bien')
    if not all([nombre, apellido, dni, email, genero, fecha_nacimiento, telefono, especialidad, matricula]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)
    
    print('Vacios no estan')

    if Medico.objects.filter(dni=dni).exists():
        return JsonResponse({"error": "El Médico ya existe"}, status=400)

    print('no existe, vamos bien')
    # Crear el rol de médico si no existe
    rol_medico, created = Rol.objects.get_or_create(rol='Medico')
    print('creamos o tomamos el rol')
    print('Vamos a crear el usuario')
    # Crear el usuario del médico
    contrasena_encriptada = make_password('12345678')
    nuevo_usuario = Usuario(idRol=rol_medico, usuario=dni, contraseña=contrasena_encriptada)
    nuevo_usuario.save()
    print('Creamos usuario')
    # Crear el médico
    nuevo_medico = Medico(
        idUsuario=nuevo_usuario,
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        email=email,
        genero=genero,
        fecha_nacimiento=fecha_nacimiento,
        telefono=telefono,
        especialidad=especialidad,
        matricula=matricula
    )
    nuevo_medico.save()

    return JsonResponse({"message": "Médico Creado con Éxito"}, status=201)

#Registrar administrativo con usuario

@csrf_exempt
@api_view(['POST'])
def registrarAdministrativo(request):
    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')
    dni = request.data.get('dni')

    if not all([nombre, apellido, dni]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    if Administrativo.objects.filter(dni=dni).exists():
        return JsonResponse({"error": "El Administrativo ya existe"}, status=400)

    # Crear el rol de administrativo si no existe
    rol_administrativo, created = Rol.objects.get_or_create(rol='Administrativo')

    # Crear el usuario del administrativo
    contrasena_encriptada = make_password('12345678')
    nuevo_usuario = Usuario(idRol=rol_administrativo, usuario=dni, contraseña=contrasena_encriptada)
    nuevo_usuario.save()

    # Crear el administrativo
    nuevo_administrativo = Administrativo(
        idUsuario=nuevo_usuario,
        nombre=nombre,
        apellido=apellido,
        dni=dni,
    )
    nuevo_administrativo.save()

    return JsonResponse({"message": "Administrativo Creado con Éxito"}, status=201)

@csrf_exempt
@api_view(['POST'])
def validar_dni_paciente(request):
    dni = request.data.get('dni')
    if not dni:
        return JsonResponse({"error": "DNI es requerido"}, status=400)
    
    try:
        paciente = Paciente.objects.get(dni=dni)
        return JsonResponse({"idPaciente": paciente.idPaciente,"nombre": paciente.nombre, "apellido": paciente.apellido}, status=200)
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

@csrf_exempt
@api_view(['GET'])
def buscar_medico_por_dni(request, dni):
    if not dni:
        return JsonResponse({"error": "DNI es requerido"}, status=400)
    
    try:
        medico = Medico.objects.get(dni=dni)
        medico_data = {
            "idMedico": medico.idMedico,
            "nombre": medico.nombre,
            "apellido": medico.apellido,
            "dni": medico.dni,
            "email": medico.email,
            "genero": medico.genero,
            "fecha_nacimiento": medico.fecha_nacimiento.strftime('%Y-%m-%d'),
            "telefono": medico.telefono,
            "especialidad": medico.especialidad,
            "matricula": medico.matricula
        }
        return JsonResponse(medico_data, status=200)
    except Medico.DoesNotExist:
        return JsonResponse({"error": "Médico no encontrado"}, status=404)

@csrf_exempt
@api_view(['GET'])
def buscar_administrativo_por_dni(request, dni):
    if not dni:
        return JsonResponse({"error": "DNI es requerido"}, status=400)
    
    try:
        admin = Administrativo.objects.get(dni=dni)
        admin_data = {
            "idAdministrativo": admin.idAdministrativo,
            "nombre": admin.nombre,
            "apellido": admin.apellido,
            "dni": admin.dni
        }
        return JsonResponse(admin_data, status=200)
    except Medico.DoesNotExist:
        return JsonResponse({"error": "Administrativo no encontrado"}, status=404)
    
@csrf_exempt
@api_view(['GET'])
def buscar_paciente_por_dni(request,dni):
    if not dni:
        return JsonResponse({"error": "DNI es requerido"}, status=400)
    
    try: 
        paciente = Paciente.objects.get(dni=dni)
        paciente_data = {
            "idPaciente": paciente.idPaciente,
            "nombre": paciente.nombre,
            "apellido": paciente.apellido,
            "dni": paciente.dni,
            "email": paciente.email,
            "fecha_nacimiento": paciente.fecha_nacimiento.strftime('%Y-%m-%d'),
            "genero": paciente.genero,
            "telefono": paciente.telefono,
            "contacto_emergencia": paciente.contacto_emergencia
        }
        return JsonResponse(paciente_data, status=200)
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)


@csrf_exempt
@api_view(['POST'])
def buscar_medicos_especialidad(request):
    especialidad = request.data.get('especialidad')
    if not especialidad:
        return JsonResponse({"error": "Especialidad es requerida"}, status=400)
    
    medicos = Medico.objects.filter(especialidad=especialidad).values('idMedico', 'nombre', 'apellido', 'dni')
    return JsonResponse(list(medicos), safe=False, status=200)

@csrf_exempt
@api_view(['POST'])
def horarios_disponibles_medico(request):
    idMedico = request.data.get('idMedico')
    fecha = request.data.get('fecha')
    if not idMedico or not fecha:
        return JsonResponse({"error": "ID del Médico y Fecha son requeridos"}, status=400)
    
    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
    if fecha_dt.weekday() >= 5:  # Sabado o Domingo
        return JsonResponse({"error": "No hay atención los fines de semana"}, status=400)
    
    horarios_ocupados = Cita.objects.filter(idMedico=idMedico, fechaCita__date=fecha_dt).values_list('fechaCita__time', flat=True)
    todos_los_horarios = [datetime.strptime(f"{hora}:00", '%H:%M').time() for hora in range(9, 19)]
    horarios_disponibles = [hora.strftime('%H:%M') for hora in todos_los_horarios if hora not in horarios_ocupados]
    
    return JsonResponse({"horarios_disponibles": horarios_disponibles}, status=200)

@csrf_exempt
@api_view(['POST'])
def crear_cita(request):
    idPaciente = request.data.get('idPaciente')
    idMedico = request.data.get('idMedico')
    fechaCita = request.data.get('fechaCita')
    estado = request.data.get('estado')
    
    if not idPaciente or not idMedico or not fechaCita:
        return JsonResponse({"error": "Todos los campos son requeridos"}, status=400)
    
    fechaCita_dt = datetime.strptime(fechaCita, '%Y-%m-%dT%H:%M:%S')
    
    if Cita.objects.filter(idMedico=idMedico, fechaCita=fechaCita_dt).exists():
        return JsonResponse({"error": "Horario no disponible"}, status=400)
    
    nueva_cita = Cita(idPaciente_id=idPaciente, idMedico_id=idMedico, fechaCita=fechaCita_dt, estado=estado)
    nueva_cita.save()
    
    return JsonResponse({"message": "Cita creada con éxito"}, status=201)


def connect_to_mongodb():
    try:
        # Conectarse a MongoDB Atlas con certificación SSL
        client = MongoClient('mongodb+srv://alejosiri:IESHe4ttyetSEKJF@cluster0.yvse3ez.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', tlsCAFile=certifi.where())
        db = client['Consultorio']
        return db 
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None
    
@csrf_exempt
@api_view(['POST'])
def agregar_historial_medico_vacio(request):
    try:
        paciente_id = request.data.get('idPaciente')
        if not paciente_id:
            return JsonResponse({'error': 'Falta el campo paciente_id'}, status=400)

        db = connect_to_mongodb()
        if db is None:
            return JsonResponse({'error': 'No se pudo conectar a MongoDB'}, status=500)

        nueva_instancia = db.Pacientes.insert_one({'paciente_id': paciente_id})
        return JsonResponse({'mensaje': 'Nueva instancia creada', 'id': str(nueva_instancia.inserted_id)}, status=201)
    except Exception as e:
        print(f"Error al agregar historial médico vacío: {e}")
        return JsonResponse({'error': 'Error al agregar historial médico vacío'}, status=500)

@csrf_exempt
@api_view(['GET'])
def getallhistoriales(request):
    db = connect_to_mongodb()
    if db is None:
        return JsonResponse({'error': 'No se pudo conectar a MongoDB'}, status=500)

    try:
        pacientes = list(db.Pacientes.find())
        if pacientes:
            context = []
            for paciente in pacientes:
                context.append({
                    'historial_id': str(paciente.get('historial_id', '')),
                    'paciente_id': paciente.get('paciente_id', ''),
                    'diagnosticos': paciente.get('diagnosticos', []),
                    'tratamientos': paciente.get('tratamientos', []),
                    'hospitalizaciones': paciente.get('hospitalizaciones', []),
                    'observaciones': paciente.get('observaciones', ''),
                })
            json_data = json.dumps(context)
            return JsonResponse(json_data, safe=False, status=200)
        else:
            return JsonResponse({'error': 'No se encontraron pacientes'}, status=404)
    except Exception as e:
        print(f"Error al consultar pacientes: {e}")
        return JsonResponse({'error': 'Error al consultar pacientes'}, status=500)
    
@csrf_exempt
@api_view(['GET'])
def getHistorialUsuario(request):
    paciente_id = request.data.get('idPaciente')
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)
    # Utilizar 'db' para realizar operaciones en tu base de datos MongoDB
    paciente = db.Pacientes.find_one({'paciente_id': paciente_id})

    # Si se encontraron pacientes, devolver los datos como contexto para renderizar en el template
    if paciente:
        context = {
            'historial_id': str(paciente.get('historial_id', '')),
            'paciente_id': paciente.get('paciente_id', ''),
            'diagnosticos': paciente.get('diagnosticos', []),
            'tratamientos': paciente.get('tratamientos', []),
            'hospitalizaciones': paciente.get('hospitalizaciones', []),
            'observaciones': paciente.get('observaciones', '')
        }
        # Convertir la lista de objetos a un formato JSON válido
        json_data = json.dumps(context)
        return JsonResponse(json_data, safe=False, status=200)
    else:
        context = {'error': 'No se encontraron pacientes'}
        return JsonResponse(context, status=404)

@csrf_exempt
@api_view(['GET'])
def get_all_tratamientos(request):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)
    # Obtener todos los tratamientos de todos los pacientes
    tratamientos = list(db.Pacientes.aggregate([
        {'$unwind': '$tratamientos'},
        {'$project': {
            '_id': 0,
            'tratamientos': 1
        }}
    ]))

    # Si se encontraron tratamientos, devolver los datos como contexto para renderizar en el template
    if tratamientos:
        context = []
        for tratamiento in tratamientos:
            context.append(tratamiento['tratamientos'])
        return JsonResponse(context, safe=False, status=200)
    else:
        context = {'error': 'No se encontraron tratamientos'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['GET'])
def get_tratamientos_by_paciente_id(request, paciente_id):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)
    # Obtener los tratamientos de un paciente por su ID
    paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})

    # Si se encontró el paciente, obtener sus tratamientos
    if paciente:
        tratamientos = paciente.get('tratamientos', [])
        json_data = json.dumps(tratamientos)
        return JsonResponse(json_data,safe=False ,status=200)
    else:
        context = {'error': 'No se encontró el paciente'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['GET'])
def get_all_hospitalizaciones(request):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)
    # Obtener todas las hospitalizaciones de todos los pacientes
    hospitalizaciones = list(db.Pacientes.aggregate([
        {'$unwind': '$hospitalizaciones'},
        {'$project': {
            '_id': 0,
            'hospitalizaciones': 1
        }}
    ]))

    # Si se encontraron hospitalizaciones, devolver los datos como contexto para renderizar en el template
    if hospitalizaciones:
        context = []
        for hospitalizacion in hospitalizaciones:
            context.append(hospitalizacion['hospitalizaciones'])
        json_data = json.dumps(context)
        return JsonResponse(json_data,safe=False, status=200)
    else:
        context = {'error': 'No se encontraron hospitalizaciones'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['GET'])
def get_hospitalizaciones_by_paciente_id(request, paciente_id):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)
    # Obtener las hospitalizaciones de un paciente por su ID
    paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})

    # Si se encontró el paciente, obtener sus hospitalizaciones
    if paciente:
        hospitalizaciones = paciente.get('hospitalizaciones', [])
        json_data = json.dumps(hospitalizaciones)
        return JsonResponse(json_data, safe=False ,status=200)
    else:
        context = {'error': 'No se encontró el paciente'}
        return JsonResponse(context, status=404)

@csrf_exempt
@api_view(['POST'])
def agregar_tratamiento(request, paciente_id):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)

    # Obtener el paciente por su ID
    paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})

    # Si se encontró el paciente, agregar un nuevo tratamiento
    if paciente:
        
        tratamiento_nuevo = {
            "tratamiento_id": ObjectId(),
            "medico_id": request.data.get('medico_id', ''),
            "descripcion": request.data.get('descripcion', ''),
            "medicacion": request.data.get('medicacion', []),
            "procedimientos": request.data.get('procedimientos', []),
            "comentarios": request.data.get('comentarios', []),
            "recomendaciones": request.data.get('recomendaciones', ''),
            "fecha_inicio": request.data.get('fecha_inicio', ''),
            "fecha_fin": request.data.get('fecha_fin', '')
        }
        # Agregar el nuevo tratamiento a la lista de tratamientos del paciente
        db.Pacientes.update_one({'paciente_id': int(paciente_id)}, {'$push': {'tratamientos': tratamiento_nuevo}})
        return JsonResponse({"message": "Tratamiento agregado correctamente"},safe=False ,status=200)
    else:
        context = {'error': 'No se encontró el paciente'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['POST'])
def agregar_hospitalizacion(request, paciente_id):


    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)

    # Obtener el paciente por su ID
    paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})

    # Si se encontró el paciente, agregar una nueva hospitalización
    if paciente:
        hospitalizacion_data = json.loads(request.body)
        hospitalizacion_nueva = {
            "hospitalizacion_id": ObjectId(),
            "medico_id": hospitalizacion_data.get('medico_id', ''),
            "fecha_ingreso": hospitalizacion_data.get('fecha_ingreso', ''),
            "fecha_alta": hospitalizacion_data.get('fecha_alta', ''),
            "detalles_tratamiento": hospitalizacion_data.get('detalles_tratamiento', '')
        }
        # Agregar la nueva hospitalización a la lista de hospitalizaciones del paciente
        db.Pacientes.update_one({'paciente_id': int(paciente_id)}, {'$push': {'hospitalizaciones': hospitalizacion_nueva}})
        return JsonResponse({"message": "Hospitalización agregada correctamente"}, safe=False,status=200)
    else:
        context = {'error': 'No se encontró el paciente'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['POST'])
def agregar_comentario_tratamiento(request, paciente_id, tratamiento_id):
    # Conectar a MongoDB
    db = connect_to_mongodb()
    print(db)

    # Obtener el paciente por su ID
    paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})
    print(paciente)
    # Si se encontró el paciente, buscar el tratamiento específico
    if paciente:

        comentario_data =request.POST
        comentario_nuevo = {
            "medico_id": comentario_data.get('medico_id', ''),
            "medico_nombre": comentario_data.get('medico_nombre', ''),
            "comentario": comentario_data.get('comentario', ''),
            "fecha": comentario_data.get('fecha', '')
        }

        # Actualizar el tratamiento específico con el nuevo comentario
        db.Pacientes.update_one(
            {'paciente_id': int(paciente_id), 'tratamientos.tratamiento_id': tratamiento_id},
            {'$push': {'tratamientos.$.comentarios': comentario_nuevo}}
        )
        
        return JsonResponse({"message": "Comentario agregado correctamente"}, status=200)
    else:
        context = {'error': 'No se encontró el paciente'}
        return JsonResponse(context, status=404)


@csrf_exempt
@api_view(['POST'])
def agregar_diagnostico(request, paciente_id):
    try:
        # Conectar a MongoDB
        db = connect_to_mongodb()
        if db is None:
            return JsonResponse({'error': 'No se pudo conectar a MongoDB'}, status=500)

        # Obtener el paciente por su ID
        paciente = db.Pacientes.find_one({'paciente_id': int(paciente_id)})
        if not paciente:
            return JsonResponse({'error': 'No se encontró el paciente'}, status=404)

        # Obtener los datos del diagnóstico desde el cuerpo de la solicitud
        fecha = request.data.get('fecha')
        diagnostico = request.data.get('diagnostico')

        if not all([fecha, diagnostico]):
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

        # Crear el nuevo diagnóstico
        nuevo_diagnostico = {
            'fecha': fecha,
            'diagnostico': diagnostico
        }

        # Actualizar el historial del paciente con el nuevo diagnóstico
        db.Pacientes.update_one(
            {'paciente_id': int(paciente_id)},
            {'$push': {'diagnosticos': nuevo_diagnostico}}
        )

        return JsonResponse({'mensaje': 'Diagnóstico agregado correctamente'}, safe=False,status=200)
    except Exception as e:
        print(f"Error al agregar diagnóstico: {e}")
        return JsonResponse({'error': 'Error al agregar diagnóstico'}, status=500)
    
# Editar paciente
@csrf_exempt
@api_view(['PUT'])
def editPaciente(request, dni):
    try:
        paciente = Paciente.objects.get(dni=dni)
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')
    email = request.data.get('email')
    fecha_nacimiento = request.data.get('fecha_nacimiento')
    genero = request.data.get('genero')
    telefono = request.data.get('telefono')
    contacto_emergencia = request.data.get('contacto_emergencia')

    if not all([nombre, apellido, email, fecha_nacimiento, genero, telefono, contacto_emergencia]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    paciente.nombre = nombre
    paciente.apellido = apellido
    paciente.email = email
    paciente.fecha_nacimiento = fecha_nacimiento
    paciente.genero = genero
    paciente.telefono = telefono
    paciente.contacto_emergencia = contacto_emergencia
    paciente.save()

    return JsonResponse({"message": "Paciente Actualizado con Éxito"}, status=200)


# Editar médico
@csrf_exempt
@api_view(['PUT'])
def editMedico(request, dni):
    try:
        medico = Medico.objects.get(dni=dni)
    except Medico.DoesNotExist:
        return JsonResponse({"error": "Médico no encontrado"}, status=404)

    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')
    email = request.data.get('email')
    genero = request.data.get('genero')
    fecha_nacimiento = request.data.get('fecha_nacimiento')
    telefono = request.data.get('telefono')
    especialidad = request.data.get('especialidad')
    matricula = request.data.get('matricula')

    if not all([nombre, apellido, email, genero, fecha_nacimiento, telefono, especialidad, matricula]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    medico.nombre = nombre
    medico.apellido = apellido
    medico.email = email
    medico.genero = genero
    medico.fecha_nacimiento = fecha_nacimiento
    medico.telefono = telefono
    medico.especialidad = especialidad
    medico.matricula = matricula
    medico.save()

    return JsonResponse({"message": "Médico Actualizado con Éxito"}, status=200)


# Editar administrativo
@csrf_exempt
@api_view(['PUT'])
def editAdministrativo(request, dni):
    try:
        administrativo = Administrativo.objects.get(dni=dni)
    except Administrativo.DoesNotExist:
        return JsonResponse({"error": "Administrativo no encontrado"}, status=404)

    nombre = request.data.get('nombre')
    apellido = request.data.get('apellido')

    if not all([nombre, apellido]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    administrativo.nombre = nombre
    administrativo.apellido = apellido
    administrativo.save()

    return JsonResponse({"message": "Administrativo Actualizado con Éxito"}, status=200)

# Eliminar paciente
@csrf_exempt
@api_view(['DELETE'])
def deletePaciente(request, dni):
    try:
        paciente = Paciente.objects.get(dni=dni)
        paciente.delete()
        return JsonResponse({"message": "Paciente Eliminado con Éxito"}, status=200)
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

# Eliminar médico
@csrf_exempt
@api_view(['DELETE'])
def deleteMedico(request, dni):
    try:
        medico = Medico.objects.get(dni=dni)
        medico.delete()
        return JsonResponse({"message": "Médico Eliminado con Éxito"}, status=200)
    except Medico.DoesNotExist:
        return JsonResponse({"error": "Médico no encontrado"}, status=404)

# Eliminar administrativo
@csrf_exempt
@api_view(['DELETE'])
def deleteAdministrativo(request, dni):
    try:
        administrativo = Administrativo.objects.get(dni=dni)
        administrativo.delete()
        return JsonResponse({"message": "Administrativo Eliminado con Éxito"}, status=200)
    except Administrativo.DoesNotExist:
        return JsonResponse({"error": "Administrativo no encontrado"}, status=404)
    
# Eliminar cita
@csrf_exempt
@api_view(['DELETE'])
def eliminarCita(request, idCita):
    try:
        cita = Cita.objects.get(idCita=idCita)
        cita.delete()
        return JsonResponse({"message": "Cita Eliminada con Éxito"}, status=200)
    except Cita.DoesNotExist:
        return JsonResponse({"error": "Cita no encontrada"}, status=404)

# Editar estado de la cita
@csrf_exempt
@api_view(['PUT'])
def editarEstadoCita(request, idCita):
    try:
        cita = Cita.objects.get(idCita=idCita)
    except Cita.DoesNotExist:
        return JsonResponse({"error": "Cita no encontrada"}, status=404)

    nuevo_estado = request.data.get('estado')
    if not nuevo_estado:
        return JsonResponse({"error": "Estado de la cita es requerido"}, status=400)

    cita.estado = nuevo_estado
    cita.save()

    return JsonResponse({"message": "Estado de la cita actualizado con éxito"}, status=200)