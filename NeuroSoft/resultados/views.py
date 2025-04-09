from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
from django.conf import settings
from estudios.models import Estudio
from .models import Resultado
from .serializers import ResultadoSerializer
import logging
from urllib.parse import urljoin
from django.core.files.base import ContentFile
import base64
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class ResultadoViewSet(viewsets.ModelViewSet):
    queryset = Resultado.objects.all().order_by('-fecha_estudio')  # Ordenar por fecha descendente
    serializer_class = ResultadoSerializer
    permission_classes = [AllowAny]  # Permitir acceso sin necesidad de autenticación
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['paciente_id', 'estado_estudio', 'prediccion_ia']
    search_fields = ['paciente_id__nombre', 'paciente_id__apellido_paterno', 'resumen_prediccion']
    ordering_fields = ['fecha_estudio', 'precision']
    ordering = ['-fecha_estudio']  # Orden por defecto

    def list(self, request, *args, **kwargs):
        """
        Lista todos los resultados con opciones de filtrado, búsqueda y ordenamiento.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Paginación
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error al listar resultados: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error al recuperar los resultados'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Obtiene un resultado específico por ID.
        """
        try:
            resultado = self.get_object()
            serializer = self.get_serializer(resultado)
            return Response(serializer.data)
        except Resultado.DoesNotExist:
            return Response(
                {'error': 'Resultado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error al recuperar resultado {pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error al recuperar el resultado'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """
        Endpoint adicional para obtener resultados por paciente.
        Ejemplo: /api/resultados/por_paciente/?paciente_id=123
        """
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Se requiere el parámetro paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resultados = Resultado.objects.filter(paciente_id=paciente_id).order_by('-fecha_estudio')
            serializer = self.get_serializer(resultados, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error al obtener resultados para paciente {paciente_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener resultados'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def procesar_imagen(self, request):
        try:
            estudio_id = request.data.get('estudio_id')
            if not estudio_id:
                return Response({'error': 'ID de estudio no proporcionado'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Obtener el estudio con select_related para optimizar
            estudio = Estudio.objects.select_related('paciente_id').get(id=estudio_id)

            # Verificar que el paciente existe
            if not estudio.paciente_id:
                return Response({'error': 'Paciente no encontrado para este estudio'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Construir URL para la API de predicción
            api_url = urljoin(settings.BASE_API_URL, 'api/neurosoft/predict/')

            # Preparar payload
            payload = {
                "file_path": estudio.ruta_archivo
            }

            # Configurar headers
            headers = {}
            if 'Authorization' in request.headers:
                headers['Authorization'] = request.headers['Authorization']

            # Llamar a la API de predicción
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            resultado_data = response.json()

            # Procesar imagen (versión más robusta)
            imagen_file = None
            ext = 'png'  # extensión por defecto

            if resultado_data.get('imagen_bytes'):
                try:
                    img_data = resultado_data['imagen_bytes']

                    # Manejar diferentes formatos de base64
                    if ';base64,' in img_data:
                        format, imgstr = img_data.split(';base64,')
                        ext = format.split('/')[-1] if '/' in format else 'png'
                    else:
                        imgstr = img_data

                    imagen_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f"resultado_{estudio_id}.{ext}"
                    )
                except Exception as e:
                    logger.error(f"Error al procesar imagen base64: {str(e)}")
                    # Continuar sin imagen si hay error

            # Crear resultado - versión corregida
            resultado = Resultado(
                paciente_id=estudio.paciente_id.id,  # Asegurar que pasamos solo el ID
                fecha_estudio=estudio.fecha_estudio,
                estado_estudio=Resultado.EstadoEstudio.FINALIZADO,
                prediccion_ia=resultado_data['prediccion'],
                precision=resultado_data['precision'],
                resumen_prediccion=resultado_data.get('resumen', '')
            )

            if imagen_file:
                resultado.imagen_estudio.save(
                    f"resultado_{estudio_id}.{ext}",
                    imagen_file
                )

            resultado.save()

            # Actualizar estudio
            estudio.procesado = True
            estudio.save()

            # Preparar respuesta
            response_data = {
                'success': True,
                'resultado_id': resultado.id,
                'prediccion': resultado.prediccion_ia,
                'precision': float(resultado.precision),
                'imagen_url': resultado.imagen_estudio.url if resultado.imagen_estudio else None,
                'resumen': resultado.resumen_prediccion,
                'probabilidades': {
                    'Poco probable': resultado_data['probabilidades'][0] * 100,
                    'Probable': resultado_data['probabilidades'][1] * 100,
                    'Muy probable': resultado_data['probabilidades'][2] * 100
                }
            }

            return Response(response_data)

        except Estudio.DoesNotExist:
            logger.error(f"Estudio no encontrado: {estudio_id}")
            return Response({'error': 'Estudio no encontrado'},
                            status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al llamar API de predicción: {str(e)}")
            return Response({'error': 'Error al procesar la imagen con el modelo de IA'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Error inesperado al procesar imagen: {str(e)}", exc_info=True)
            return Response({'error': 'Error interno del servidor'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'])
    def resultado_por_estudio(self, request):
        """
        Obtiene el resultado asociado a un estudio específico por ID del estudio.
        Ejemplo: /api/resultados/resultado_por_estudio/?estudio_id=123
        """
        estudio_id = request.query_params.get('estudio_id')
        if not estudio_id:
            return Response(
                {'error': 'Se requiere el parámetro estudio_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            estudio = Estudio.objects.get(id=estudio_id)
            resultado = Resultado.objects.get(paciente_id=estudio.paciente_id, fecha_estudio=estudio.fecha_estudio)
            serializer = self.get_serializer(resultado)
            return Response(serializer.data)
        except Estudio.DoesNotExist:
            return Response(
                {'error': 'Estudio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Resultado.DoesNotExist:
            return Response(
                {'error': 'Resultado no encontrado para el estudio especificado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error al obtener resultado para estudio {estudio_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener el resultado'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from estudios.models import Estudio
from .models import Resultado
import logging
from rest_framework import serializers

logger = logging.getLogger(__name__)

class ResultadoDetalladoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultado
        fields = '__all__'
        depth = 1  
import json
class ConsultaResultadoView(APIView):
    """
    Endpoint para consultar resultados de un estudio en formato específico
    GET /api/consulta-resultado/?estudio_id=123
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estudio_id = request.query_params.get('estudio_id')
        if not estudio_id:
            return Response(
                {'error': 'Se requiere el parámetro estudio_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            estudio = Estudio.objects.get(id=estudio_id)
            resultado = Resultado.objects.get(
                paciente_id=estudio.paciente_id,
                fecha_estudio=estudio.fecha_estudio
            )

            response_data = {
                "success": True,
                "resultado_id": resultado.id,
                "prediccion": resultado.prediccion_ia,
                "precision": float(resultado.precision),
                "imagen_url": resultado.imagen_estudio.url if resultado.imagen_estudio else None,
                "resumen": resultado.resumen_prediccion,
                "probabilidades": json.loads(resultado.probabilidades) if resultado.probabilidades else {}
            }

            return Response(response_data)

        except Estudio.DoesNotExist:
            logger.error(f"Estudio no encontrado: {estudio_id}")
            return Response(
                {'success': False, 'error': 'Estudio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Resultado.DoesNotExist:
            logger.error(f"Resultado no encontrado para estudio: {estudio_id}")
            return Response(
                {'success': False, 'error': 'Resultado no encontrado para este estudio'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error al consultar resultado {estudio_id}: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


import uuid
class ProcesarImagenView(APIView):
    """
    Endpoint para procesar imágenes y obtener resultados
    POST /api/procesar-imagen/
    {
        "estudio_id": 123
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            estudio_id = request.data.get('estudio_id')
            if not estudio_id:
                return Response(
                    {'success': False, 'error': 'ID de estudio no proporcionado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            estudio = Estudio.objects.select_related('paciente_id').get(id=estudio_id)
            
            if not estudio.paciente_id:
                return Response(
                    {'success': False, 'error': 'Paciente no encontrado para este estudio'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Aquí iría tu lógica para llamar al modelo de IA
            # Esto es un ejemplo - reemplaza con tu implementación real
            resultado_data = {
                'prediccion': 'Muy probable',
                'precision': 99.99991655349731,
                'imagen_bytes': '...',  # Tu dato real de imagen en base64
                'resumen': 'Predicción: Muy probable (100.00%)\nDistribución: Poco probable: 0.00%, Probable: 0.00%, Muy probable: 100.00%',
                'probabilidades': [8.105013762360613e-05, 1.404403676685817e-08, 99.99991655349731]
            }

            # Procesar imagen
            imagen_file = None
            ext = 'png'
            
            if resultado_data.get('imagen_bytes'):
                try:
                    img_data = resultado_data['imagen_bytes']
                    
                    if ';base64,' in img_data:
                        format, imgstr = img_data.split(';base64,')
                        ext = format.split('/')[-1] if '/' in format else 'png'
                    else:
                        imgstr = img_data
                    
                    imagen_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f"resultado_{estudio_id}.{ext}"
                    )
                except Exception as e:
                    logger.error(f"Error al procesar imagen base64: {str(e)}")

            # Crear resultado
            resultado = Resultado(
                paciente_id=estudio.paciente_id.id,
                fecha_estudio=estudio.fecha_estudio,
                estado_estudio=Resultado.EstadoEstudio.FINALIZADO,
                prediccion_ia=resultado_data['prediccion'],
                precision=resultado_data['precision'],
                resumen_prediccion=resultado_data.get('resumen', ''),
                probabilidades={
                    'Poco probable': resultado_data['probabilidades'][0],
                    'Probable': resultado_data['probabilidades'][1],
                    'Muy probable': resultado_data['probabilidades'][2]
                }
            )

            if imagen_file:
                resultado.imagen_estudio.save(
                    f"resultado_{estudio_id}_{uuid.uuid4().hex[:8]}.{ext}",
                    imagen_file
                )

            resultado.save()

            # Actualizar estudio
            estudio.procesado = True
            estudio.save()

            # Preparar respuesta
            response_data = {
                "success": True,
                "resultado_id": resultado.id,
                "prediccion": resultado.prediccion_ia,
                "precision": float(resultado.precision),
                "imagen_url": resultado.imagen_estudio.url if resultado.imagen_estudio else None,
                "resumen": resultado.resumen_prediccion,
                "probabilidades": {
                    "Poco probable": resultado.probabilidades['Poco probable'],
                    "Probable": resultado.probabilidades['Probable'],
                    "Muy probable": resultado.probabilidades['Muy probable']
                }
            }

            return Response(response_data)

        except Estudio.DoesNotExist:
            logger.error(f"Estudio no encontrado: {estudio_id}")
            return Response(
                {'success': False, 'error': 'Estudio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error inesperado al procesar imagen: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )