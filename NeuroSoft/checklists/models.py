from django.db import models
from pacientes.models import Paciente

class ChecklistCausas(models.Model):
    paciente_id = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    traumatismo_cabeza = models.BooleanField(default=False)
    presion_alta = models.BooleanField(default=False)
    colesterol_alto = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    antecedentes_familiares = models.BooleanField(default=False)
    enfermedad_cardiovascular = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Checklists de Causas"

class ChecklistEmergencia(models.Model):
    paciente_id= models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dificultad_hablar = models.BooleanField(default=False)
    entumecimiento_cara = models.BooleanField(default=False)
    entumecimiento_brazo = models.BooleanField(default=False)
    problemas_ver = models.BooleanField(default=False)
    dolor_cabeza = models.BooleanField(default=False)
    problemas_caminar = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Checklists de Emergencia"