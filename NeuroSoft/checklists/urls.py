from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChecklistCausasViewSet, ChecklistEmergenciaViewSet

router = DefaultRouter()
router.register(r'causas', ChecklistCausasViewSet, basename='checklist-causas')
router.register(r'emergencia', ChecklistEmergenciaViewSet, basename='checklist-emergencia')

urlpatterns = [
    path('', include(router.urls)),
]