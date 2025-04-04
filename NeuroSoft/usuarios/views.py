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
        if self.action in ['create', 'login', 'logout']:
            return [AllowAny()]
        elif self.action == 'list':  # Cambiamos para permitir usuarios autenticados
            return [IsAuthenticated()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    # Método GET personalizado para obtener todos los usuarios
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def get_usuarios(self, request):
        """
        Endpoint para obtener todos los usuarios (solo administradores)
        """
        usuarios = Usuario.objects.all()
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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