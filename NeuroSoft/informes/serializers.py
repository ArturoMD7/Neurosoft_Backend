# informes/serializers.py

from rest_framework import serializers
from resultados.models import Resultado  # Ajusta el nombre de la app si es diferente

class ResultadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultado
        fields = [
            'id',
            'nombre_paciente',
            'fecha_estudio',
            'fecha_reporte',
            'datos_checklist',
            'estado_analisis',
            'resultado_prediccion',
            'precision',
            'probabilidades'
        ]
