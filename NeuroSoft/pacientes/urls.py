# pacientes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PacienteViewSet

router = DefaultRouter()
router.register(r'', PacienteViewSet, basename='paciente')  # Registra todas las rutas CRUD

urlpatterns = [
    path('', include(router.urls)),  # Incluye las rutas generadas por el router
]