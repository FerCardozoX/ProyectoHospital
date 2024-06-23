from django.urls import path
from .views import *

urlpatterns = [
    path('getpacientes/',getPacientes , name='getPacientes'),
    path('getmedicos/',getMedicos , name='getMedicos'),
    path('getcitas/',getCitas , name='getCitas'),
    path('postCrearPaciente/', postCrearPaciente, name='crearPaciente'),
    path('registrarMedico/', registrar_Medico, name='registrarMedico'),
    path('registrarAdministrativo/', registrarAdministrativo, name='crearAdministrativo'),
    path('validarDniPaciente/', validar_dni_paciente, name='validardnipaciente'),
    path('buscarmedicosespecialidad/', buscar_medicos_especialidad, name='buscarmedicosespecialidad'),
    path('horariosDisponiblesMedico/', horarios_disponibles_medico, name='horariosdisponiblesmedico'),
    path('buscarPacientePorDni/<str:dni>/', buscar_paciente_por_dni, name='buscarpacientepordni'),
    path('buscarMedicoPorDni/<str:dni>/', buscar_medico_por_dni, name='buscarmedicopordni'),
    path('crearCita/', crear_cita, name='crearcita'),
]
