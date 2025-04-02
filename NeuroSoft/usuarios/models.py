from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'Admin', _('Administrador')
        MEDICO = 'Médico', _('Médico')
    
    # Cambiar 'correo' por 'email' para mantener consistencia con AbstractUser
    email = models.EmailField(_('email address'), unique=True)  # Cambio clave aquí
    rol = models.CharField(
        _('rol'), 
        max_length=6, 
        choices=Roles.choices,
        default=Roles.MEDICO
    )
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    es_activo = models.BooleanField(_('activo'), default=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'rol']
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['last_name', 'first_name']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"