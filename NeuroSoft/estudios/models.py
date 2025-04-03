from django.db import models
from pacientes.models import Paciente
from checklists.models import ChecklistCausas, ChecklistEmergencia

class Estudio(models.Model):
    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    
    paciente_id = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='paciente_id', verbose_name='Paciente')
    fecha_estudio = models.DateField()
    sede = models.CharField(max_length=100)
    prioridad = models.CharField(max_length=5, choices=PRIORIDAD_CHOICES, default='Media')
    checklist_causas = models.ForeignKey(ChecklistCausas, on_delete=models.SET_NULL, null=True)
    checklist_emergencia = models.ForeignKey(ChecklistEmergencia, on_delete=models.SET_NULL, null=True)
    ruta_archivo = models.CharField(max_length=500, null=True, blank=True)  # Cambiamos BinaryField por CharField
    
    class Meta:
        verbose_name_plural = "Estudios"