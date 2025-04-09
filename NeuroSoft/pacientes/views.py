from rest_framework import viewsets
from .models import Paciente
from .serializers import PacienteSerializer 
from rest_framework.permissions import AllowAny


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [AllowAny]  # Permitir acceso sin necesidad de autenticación