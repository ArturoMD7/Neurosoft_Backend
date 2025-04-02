from django.db import models
from pacientes.models import Paciente
from django.utils.translation import gettext_lazy as _

class Resultado(models.Model):
    class EstadoEstudio(models.TextChoices):
        PENDIENTE = 'Pendiente', _('Pendiente')
        EN_PROCESO = 'En Proceso', _('En Proceso')
        FINALIZADO = 'Finalizado', _('Finalizado')
    
    class Prediccion(models.TextChoices):
        POCO_PROBABLE = 'Poco probable', _('Poco probable')
        PROBABLE = 'Probable', _('Probable')
        MUY_PROBABLE = 'Muy probable', _('Muy probable')
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        verbose_name=_('Paciente'),
        related_name='resultados'
    )
    fecha_estudio = models.DateField(
        verbose_name=_('Fecha del estudio')
    )
    fecha_resultado = models.DateField(
        verbose_name=_('Fecha del resultado'),
        auto_now_add=True
    )
    estado_estudio = models.CharField(
        max_length=20,
        choices=EstadoEstudio.choices,
        default=EstadoEstudio.PENDIENTE,
        verbose_name=_('Estado del estudio')
    )
    prediccion_ia = models.CharField(
        max_length=15,
        choices=Prediccion.choices,
        verbose_name=_('Predicción de IA')
    )
    precision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_('Precisión (%)')
    )
    imagen_estudio = models.ImageField(
        upload_to='resultados/imagenes/',
        null=True,
        blank=True,
        verbose_name=_('Imagen de referencia')
    )
    resumen_prediccion = models.TextField(
        verbose_name=_('Resumen de la predicción'),
        blank=True,
        null=True
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )

    class Meta:
        verbose_name = _('Resultado')
        verbose_name_plural = _('Resultados')
        ordering = ['-fecha_estudio', '-creado_en']
        indexes = [
            models.Index(fields=['fecha_estudio']),
            models.Index(fields=['estado_estudio']),
            models.Index(fields=['prediccion_ia']),
        ]

    def __str__(self):
        return f"Resultado {self.id} - {self.paciente} ({self.fecha_estudio})"

    @property
    def precision_porcentaje(self):
        return f"{self.precision}%"

    def save(self, *args, **kwargs):
        # Lógica adicional antes de guardar si es necesaria
        super().save(*args, **kwargs)