from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Agency, AgencyUser
import re
from urllib.parse import quote


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
    whatsapp_link = serializers.SerializerMethodField()
    
    class Meta:
        model = Agency
        fields = [
            'id', 'name', 'city', 'address', 'phone', 'whatsapp', 'whatsapp_link', 'email', 'website', 
            'description', 'status', 'is_verified', 'verification_date', 'users', 'created_at'
        ]
        read_only_fields = ['status', 'is_verified', 'verification_date', 'created_at']

    def get_whatsapp_link(self, agency: Agency) -> str | None:
        """Return a wa.me link with a prefilled French message if whatsapp is set."""
        if not agency.whatsapp:
            return None

        # Build E.164-like digits-only string for wa.me (no plus sign)
        digits_only = re.sub(r"\D", "", agency.whatsapp)
        if not digits_only:
            return None

        default_message = (
            f"Bonjour {agency.name}, je souhaite vous contacter via AutoPlatform."
        )
        encoded_message = quote(default_message, safe="")
        return f"https://wa.me/{digits_only}?text={encoded_message}"


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
