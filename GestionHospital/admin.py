from django.contrib import admin
from .models import Rol, Usuario, Medico, Paciente, Administrativo, Cita

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Administrativo)
admin.site.register(Cita)
