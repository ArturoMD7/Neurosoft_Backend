from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

        extra_kwargs = {
            'apellido_materno': {'required': False},  # Ejemplo
        }