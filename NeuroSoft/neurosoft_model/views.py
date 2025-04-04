from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from .predictors import DerramePredictor

# Instancia única del predictor
derrame_predictor = DerramePredictor()

@csrf_exempt
def predict_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_path = data.get('file_path')

            if not file_path:
                return JsonResponse({'error': 'Falta la ruta del archivo'}, status=400)

            result = derrame_predictor.predict(file_path)

            # Convertir imagen a Base64 solo si existe
            if result.get('imagen_bytes'):
                result['imagen_bytes'] = base64.b64encode(result['imagen_bytes']).decode('utf-8')

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': f"Error en la predicción: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)
