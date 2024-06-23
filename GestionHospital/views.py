from datetime import datetime, time
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password,check_password
from .models import *



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

    return JsonResponse({"message": "Paciente Creado con Éxito"}, status=201)

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
    email = request.data.get('email')
    genero = request.data.get('genero')
    fecha_nacimiento = request.data.get('fecha_nacimiento')
    telefono = request.data.get('telefono')

    if not all([nombre, apellido, dni, email, genero, fecha_nacimiento, telefono]):
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
        apellido=apellido
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
        return JsonResponse({"nombre": paciente.idPaciente,"nombre": paciente.nombre, "apellido": paciente.apellido}, status=200)
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