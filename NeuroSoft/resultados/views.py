from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from neurosoft_model.predictors import DerramePredictor
from .models import Resultado
from .serializers import ResultadoSerializer
from estudios.models import Estudio
import base64
import logging

logger = logging.getLogger(__name__)

class ResultadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Resultados
    """
    queryset = Resultado.objects.all()
    serializer_class = ResultadoSerializer

    @action(detail=False, methods=['post'])
    def procesar_imagen(self, request):
        try:
            estudio_id = request.data.get('estudio_id')
            if not estudio_id:
                return Response({'error': 'ID de estudio no proporcionado'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            estudio = Estudio.objects.get(id=estudio_id)
            predictor = DerramePredictor()
            resultado_data = predictor.predict(estudio.ruta_archivo)

            # Convertir imagen a base64 para la API
            imagen_base64 = None
            if resultado_data['imagen_bytes']:
                imagen_base64 = base64.b64encode(resultado_data['imagen_bytes']).decode('utf-8')

            # Crear registro de resultado
            resultado = Resultado.objects.create(
                paciente=estudio.paciente_id,
                fecha_estudio=estudio.fecha_estudio,
                fecha_resultado=timezone.now().date(),
                estado_estudio=resultado_data['estado'],
                prediccion_ia=resultado_data['prediccion'],
                precision=resultado_data['precision'],
                imagen_estudio=resultado_data['imagen_bytes'],
                resumen_prediccion=resultado_data['resumen']
            )

            # Actualizar estado del estudio
            estudio.procesado = True
            estudio.save()

            return Response({
                'success': True,
                'resultado_id': resultado.id,
                'prediccion': resultado_data['prediccion'],
                'precision': resultado_data['precision'],
                'imagen_base64': imagen_base64,
                'resumen': resultado_data['resumen'],
                'probabilidades': {
                    'Poco probable': resultado_data['probabilidades'][0] * 100,
                    'Probable': resultado_data['probabilidades'][1] * 100,
                    'Muy probable': resultado_data['probabilidades'][2] * 100
                }
            })

        except Estudio.DoesNotExist:
            logger.error(f"Estudio no encontrado: {estudio_id}")
            return Response({'error': 'Estudio no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error al procesar imagen: {str(e)}")
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_POST
def procesar_estudio(request, estudio_id):
    try:
        estudio = Estudio.objects.get(id=estudio_id)
        predictor = DerramePredictor()
        resultado_data = predictor.predict(estudio.ruta_archivo)

        resultado = Resultado.objects.create(
            paciente=estudio.paciente_id,
            fecha_estudio=estudio.fecha_estudio,
            fecha_resultado=timezone.now().date(),
            estado_estudio=resultado_data['estado'],
            prediccion_ia=resultado_data['prediccion'],
            precision=resultado_data['precision'],
            imagen_estudio=resultado_data['imagen_bytes'],
            resumen_prediccion=resultado_data['resumen']
        )

        estudio.procesado = True
        estudio.save()

        return JsonResponse({
            'success': True,
            'resultado_id': resultado.id,
            'prediccion': resultado.prediccion_ia,
            'precision': resultado.precision
        })

    except Estudio.DoesNotExist:
        return JsonResponse({'error': 'Estudio no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)