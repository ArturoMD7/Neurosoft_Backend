from rest_framework import serializers
from .models import Estudio

class EstudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = '__all__'
        extra_kwargs = {
            'paciente_id': {'required': True},
            'checklist_causas': {'required': False},
            'checklist_emergencia': {'required': False}
        }