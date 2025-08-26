from rest_framework import serializers
from datetime import datetime, date
from .models import Booking, BookingNotification
from cars.serializers import ListingSerializer
from agencies.serializers import AgencySerializer


class BookingNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingNotification
        fields = [
            'id', 'notification_type', 'sent_to', 'subject', 'message',
            'is_sent', 'sent_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['created_at', 'sent_at']


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    agency = AgencySerializer(read_only=True)
    notifications = BookingNotificationSerializer(many=True, read_only=True)
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'agency', 'kind', 'status', 'customer_name', 'phone', 'email', 
            'start_date', 'end_date', 'test_drive_date', 'special_requests', 'total_price', 
            'deposit_amount', 'admin_notes', 'duration_days', 'notifications', 'created_at', 
            'updated_at', 'confirmed_at', 'cancelled_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'confirmed_at', 'cancelled_at']
    
    def get_duration_days(self, obj):
        return obj.duration_days


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'listing', 'kind', 'customer_name', 'phone', 'email', 'start_date', 'end_date', 
            'test_drive_date', 'special_requests'
        ]
    
    def validate(self, data):
        listing = data.get('listing')
        kind = data.get('kind')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        test_drive_date = data.get('test_drive_date')
        
        # Validate rental bookings
        if kind == 'rent':
            if not start_date:
                raise serializers.ValidationError("La date de début est requise pour une location.")
            
            if not end_date:
                raise serializers.ValidationError("La date de fin est requise pour une location.")
            
            if start_date >= end_date:
                raise serializers.ValidationError("La date de fin doit être postérieure à la date de début.")
            
            if start_date < date.today():
                raise serializers.ValidationError("La date de début ne peut pas être dans le passé.")
            
            # Check if listing is for rent
            if listing.type != 'rent':
                raise serializers.ValidationError("Cette annonce n'est pas disponible à la location.")
        
        # Validate test drive bookings
        elif kind == 'test_drive':
            if not test_drive_date:
                raise serializers.ValidationError("La date et heure d'essai sont requises.")
            
            if test_drive_date < datetime.now():
                raise serializers.ValidationError("La date d'essai ne peut pas être dans le passé.")
            
            # Check if listing is for sale
            if listing.type != 'sale':
                raise serializers.ValidationError("Cette annonce n'est pas disponible à la vente.")
        
        return data
    
    def validate_phone(self, value):
        # Basic phone validation
        if not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit commencer par '+'.")
        return value


class BookingStatsSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    recent_bookings = serializers.IntegerField()
    rental_bookings = serializers.IntegerField()
    test_drive_bookings = serializers.IntegerField()
