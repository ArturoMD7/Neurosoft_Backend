from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action in ['create', 'login', 'logout']:
            return [AllowAny()]
        elif self.action == 'list' or self.action == 'me':
            return [IsAuthenticated()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated()] # no se requiere IsAdminUser
        elif self.action == 'destroy':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated]) #permite a usuarios autenticados ver la lista
    def get_usuarios(self, request):
        """Endpoint para obtener todos los usuarios (solo administradores)"""
        if request.user.rol == 'Admin':
            usuarios = Usuario.objects.all()
            serializer = self.get_serializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No tienes permiso para ver la lista de usuarios"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint para autenticación JWT"""
        serializer = UsuarioLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

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
        return Response({"detail": "Sesión cerrada correctamente"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint para obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Endpoint para eliminar un usuario por ID.
        - Los administradores pueden eliminar cualquier usuario.
        - Los usuarios normales solo pueden eliminarse a sí mismos.
        """
        try:
            user_to_delete = Usuario.objects.get(pk=pk)
            current_user = request.user

            if current_user.rol != 'Admin' and current_user.id != user_to_delete.id:
                return Response({"detail": "No tienes permiso para eliminar este usuario"}, status=status.HTTP_403_FORBIDDEN)

            user_to_delete.delete()

            if current_user.id == user_to_delete.id:
                logout(request)
                return Response({"detail": "Tu cuenta ha sido eliminada correctamente"}, status=status.HTTP_200_OK)

            return Response({"detail": "Usuario eliminado correctamente"}, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Error al eliminar el usuario: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)