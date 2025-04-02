from rest_framework import serializers
from .models import ChecklistCausas, ChecklistEmergencia

class ChecklistCausasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistCausas
        fields = '__all__'

class ChecklistEmergenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistEmergencia
        fields = '__all__'