from django.db import models

# Create your models here.

class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    rol = models.CharField(max_length=30)
    def __str__(self):
        return self.rol
    class Meta:
        db_table = 'Rol'

class Usuario(models.Model):
    idUsuario = models.AutoField(primary_key=True)
    idRol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    usuario = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=200)
    class Meta:
        db_table = 'Usuario'

class Paciente(models.Model):
    idPaciente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    fecha_nacimiento = models.DateTimeField()
    genero = models.CharField(max_length=20)
    telefono = models.CharField(max_length=30)
    contacto_emergencia = models.CharField(max_length=30)
    def __str__(self):
        return self.apellido +' '+ self.nombre+' '+ self.dni
    class Meta:
        db_table = 'Paciente'
    
class Medico(models.Model):
    idMedico = models.AutoField(primary_key=True)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    genero = models.CharField(max_length=20)
    fecha_nacimiento = models.DateTimeField()
    telefono = models.CharField(max_length=30)
    especialidad = models.CharField(max_length=50)
    matricula = models.CharField(max_length=10)
    class Meta:
        db_table = 'Medico'

class Administrativo(models.Model):
    idAdministrativo = models.AutoField(primary_key=True)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    class Meta:
        db_table = 'Administrativo'

class Cita(models.Model):
    idCita = models.AutoField(primary_key=True)
    idPaciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    idMedico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fechaCita = models.DateTimeField()
    estado = models.CharField(max_length=20)
    class Meta:
        db_table = 'Cita'