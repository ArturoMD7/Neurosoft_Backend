from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstudioViewSet

router = DefaultRouter()
router.register(r'estudios', EstudioViewSet, basename='estudios')

urlpatterns = [
    path('', include(router.urls)),
]