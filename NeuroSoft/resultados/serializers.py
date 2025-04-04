from rest_framework import serializers
from .models import Resultado
from django.urls import reverse

class ResultadoSerializer(serializers.ModelSerializer):
    precision_porcentaje = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Resultado
        fields = '__all__'
        read_only_fields = ('creado_en', 'actualizado_en', 'fecha_resultado')
    
    def get_precision_porcentaje(self, obj):
        return f"{obj.precision}%"
    
    def get_imagen_url(self, obj):
        if obj.imagen_estudio:
            return obj.imagen_estudio.url
        return None