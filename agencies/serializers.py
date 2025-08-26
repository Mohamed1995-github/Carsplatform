from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Agency, AgencyUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AgencyUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AgencyUser
        fields = ['id', 'user', 'role', 'is_active', 'phone', 'position', 'created_at']
        read_only_fields = ['created_at']


class AgencySerializer(serializers.ModelSerializer):
    users = AgencyUserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Agency
        fields = [
            'id', 'name', 'city', 'address', 'phone', 'whatsapp', 'email', 'website', 
            'description', 'status', 'is_verified', 'verification_date', 'users', 'created_at'
        ]
        read_only_fields = ['status', 'is_verified', 'verification_date', 'created_at']


class AgencyRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True)
    
    class Meta:
        model = Agency
        fields = [
            'name', 'city', 'address', 'phone', 'whatsapp', 'email', 'website', 
            'description', 'kbis_rc', 'user'
        ]
    
    def validate_user(self, value):
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Le champ '{field}' est requis pour l'utilisateur.")
        
        # Check if username already exists
        if User.objects.filter(username=value['username']).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà.")
        
        # Check if email already exists
        if User.objects.filter(email=value['email']).exists():
            raise serializers.ValidationError("Cet email existe déjà.")
        
        return value
    
    def validate_phone(self, value):
        # Basic phone validation
        if not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit commencer par '+'.")
        return value


class AgencyStatsSerializer(serializers.Serializer):
    total_cars = serializers.IntegerField()
    active_listings = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    total_inquiries = serializers.IntegerField()
    unread_inquiries = serializers.IntegerField()
