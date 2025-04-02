from rest_framework import viewsets, permissions
from .models import Estudio
from .serializers import EstudioSerializer

class EstudioViewSet(viewsets.ModelViewSet):
    queryset = Estudio.objects.all()
    serializer_class = EstudioSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']  # Explicitamente permite POST
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)