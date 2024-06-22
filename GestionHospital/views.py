from django.http import JsonResponse
from rest_framework import viewsets, generics
from .models import Paciente, Medico, Cita

#GetAll

def getPacientes(request):
    pacientes = Paciente.objects.all().values()
    return JsonResponse(list(pacientes), status=200, safe=False)

def getMedico(request):
    Medicos = Medico.objects.all().values()
    return JsonResponse(list(Medicos), status=200, safe=False)

def getCita(request):
    Citas = Cita.objects.all().values()
    return JsonResponse(list(Citas), status=200, safe=False)

