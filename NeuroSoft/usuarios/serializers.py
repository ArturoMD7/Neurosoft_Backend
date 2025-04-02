from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'email', 'password', 'password2', 'rol', 
            'telefono', 'es_activo'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "Este correo electrónico ya está registrado"}
            )
        
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = Usuario.objects.create_user(**validated_data)
        return user

class UsuarioLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                msg = _('No se puede autenticar con las credenciales proporcionadas')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('Cuenta de usuario desactivada')
                raise serializers.ValidationError(msg, code='authorization')
            
            attrs['user'] = user
            return attrs
        
        msg = _('Debe incluir "username" y "password"')
        raise serializers.ValidationError(msg, code='authorization')