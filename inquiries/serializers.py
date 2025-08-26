from rest_framework import serializers
from .models import Inquiry, InquiryResponse
from cars.serializers import ListingSerializer
from agencies.serializers import AgencySerializer


class InquiryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryResponse
        fields = [
            'id', 'response_text', 'is_internal', 'created_at'
        ]
        read_only_fields = ['created_at']


class InquirySerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    agency = AgencySerializer(read_only=True)
    responses = InquiryResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Inquiry
        fields = [
            'id', 'listing', 'agency', 'customer_name', 'phone', 'email', 'subject', 
            'message', 'status', 'priority', 'source', 'admin_notes', 'responses', 
            'created_at', 'updated_at', 'read_at', 'replied_at', 'closed_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'read_at', 'replied_at', 'closed_at']


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            'listing', 'agency', 'customer_name', 'phone', 'email', 'subject', 'message'
        ]
    
    def validate(self, data):
        listing = data.get('listing')
        agency = data.get('agency')
        
        # Ensure either listing or agency is provided
        if not listing and not agency:
            raise serializers.ValidationError("Vous devez spécifier soit une annonce soit une agence.")
        
        if listing and agency:
            raise serializers.ValidationError("Vous ne pouvez pas spécifier à la fois une annonce et une agence.")
        
        return data
    
    def validate_phone(self, value):
        # Basic phone validation
        if not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit commencer par '+'.")
        return value


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            'customer_name', 'phone', 'email', 'subject', 'message'
        ]
    
    def create(self, validated_data):
        # Set default values for contact form
        validated_data['source'] = 'contact_form'
        validated_data['priority'] = 'normal'
        
        # Assign to a default agency (you might want to make this configurable)
        from agencies.models import Agency
        try:
            default_agency = Agency.objects.filter(status='approved').first()
            if default_agency:
                validated_data['agency'] = default_agency
        except Agency.DoesNotExist:
            pass
        
        return super().create(validated_data)
    
    def validate_phone(self, value):
        # Basic phone validation
        if not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit commencer par '+'.")
        return value


class InquiryStatsSerializer(serializers.Serializer):
    total_inquiries = serializers.IntegerField()
    new_inquiries = serializers.IntegerField()
    read_inquiries = serializers.IntegerField()
    replied_inquiries = serializers.IntegerField()
    closed_inquiries = serializers.IntegerField()
    spam_inquiries = serializers.IntegerField()
    high_priority_inquiries = serializers.IntegerField()
    recent_inquiries = serializers.IntegerField()

