from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    curp = models.CharField(max_length=18, unique=True)
    nss = models.CharField(max_length=11, unique=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    class Meta:
        verbose_name_plural = "Pacientes"