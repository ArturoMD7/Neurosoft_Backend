from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultadoViewSet, procesar_estudio

router = DefaultRouter()
router.register(r'resultados', ResultadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('procesar-estudio/<int:estudio_id>/', procesar_estudio, name='procesar_estudio'),
    path('procesar-imagen/', ResultadoViewSet.as_view({'post': 'procesar_imagen'}), name='procesar_imagen'),
]