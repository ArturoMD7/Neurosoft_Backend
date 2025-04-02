from rest_framework import viewsets
from .models import ChecklistCausas, ChecklistEmergencia
from .serializers import ChecklistCausasSerializer, ChecklistEmergenciaSerializer

class ChecklistCausasViewSet(viewsets.ModelViewSet):
    queryset = ChecklistCausas.objects.all()
    serializer_class = ChecklistCausasSerializer

class ChecklistEmergenciaViewSet(viewsets.ModelViewSet):
    queryset = ChecklistEmergencia.objects.all()
    serializer_class = ChecklistEmergenciaSerializer