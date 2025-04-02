from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        """
        Asigna permisos según la acción:
        - Crear usuario y login: Acceso público
        - Ver perfil propio: Usuario autenticado
        - Operaciones CRUD: Solo admin
        """
        if self.action in ['create', 'login', 'logout']:
            return [AllowAny()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint para autenticación JWT"""
        serializer = UsuarioLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Opcional: iniciar sesión para mantener compatibilidad con sesiones
        login(request, user)
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'nombre_completo': user.get_full_name(),
                'email': user.email,
                'rol': user.rol
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Endpoint para cerrar sesión (opcional para JWT)"""
        logout(request)
        return Response(
            {"detail": "Sesión cerrada correctamente"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint para obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)