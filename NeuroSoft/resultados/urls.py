from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultadoViewSet
from .views import ConsultaResultadoView

router = DefaultRouter()
router.register(r'resultados', ResultadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('procesar-imagen/', ResultadoViewSet.as_view({'post': 'procesar_imagen'}), name='procesar_imagen'),
    path('consulta-resultado/', ConsultaResultadoView.as_view(), name='consulta_resultado'),
]