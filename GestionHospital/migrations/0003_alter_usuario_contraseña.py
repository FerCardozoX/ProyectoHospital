# Generated by Django 5.0.6 on 2024-06-23 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionHospital', '0002_remove_paciente_idusuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='contraseña',
            field=models.CharField(max_length=200),
        ),
    ]
