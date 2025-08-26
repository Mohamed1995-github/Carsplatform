from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date
from .models import Booking, BookingNotification
from .serializers import BookingSerializer, BookingCreateSerializer, BookingNotificationSerializer


class BookingListView(generics.ListAPIView):
    """List all bookings (admin only)"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['-created_at']


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking"""
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        booking = serializer.save()
        
        # Create notification for agency
        BookingNotification.objects.create(
            booking=booking,
            notification_type='email',
            sent_to=booking.agency.email,
            subject=f"Nouvelle réservation - {booking.listing.car}",
            message=f"Une nouvelle réservation a été créée pour {booking.listing.car} par {booking.customer_name}."
        )
        
        # Create WhatsApp notification if available
        if booking.agency.whatsapp:
            BookingNotification.objects.create(
                booking=booking,
                notification_type='whatsapp',
                sent_to=booking.agency.whatsapp,
                message=f"Nouvelle réservation: {booking.customer_name} - {booking.listing.car}"
            )


class BookingConfirmView(generics.UpdateAPIView):
    """Confirm a booking (agency only)"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        
        # Create notification for customer
        BookingNotification.objects.create(
            booking=booking,
            notification_type='email',
            sent_to=booking.email,
            subject="Réservation confirmée",
            message=f"Votre réservation pour {booking.listing.car} a été confirmée."
        )
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class BookingCancelView(generics.UpdateAPIView):
    """Cancel a booking"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Create notification for customer
        BookingNotification.objects.create(
            booking=booking,
            notification_type='email',
            sent_to=booking.email,
            subject="Réservation annulée",
            message=f"Votre réservation pour {booking.listing.car} a été annulée."
        )
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class AgencyBookingsView(generics.ListAPIView):
    """Get bookings for a specific agency"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_id')
        return Booking.objects.filter(agency_id=agency_id).order_by('-created_at')


class BookingNotificationsView(generics.ListAPIView):
    """Get notifications for a booking"""
    serializer_class = BookingNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        booking_id = self.kwargs.get('booking_id')
        return BookingNotification.objects.filter(booking_id=booking_id).order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def booking_stats(request, agency_id):
    """Get booking statistics for an agency"""
    from django.db.models import Count, Q
    from datetime import timedelta
    
    # Get date range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get bookings for the agency
    bookings = Booking.objects.filter(agency_id=agency_id)
    
    stats = {
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'recent_bookings': bookings.filter(created_at__date__gte=start_date).count(),
        'rental_bookings': bookings.filter(kind='rent').count(),
        'test_drive_bookings': bookings.filter(kind='test_drive').count(),
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_booking_notification(request, booking_id):
    """Send a notification for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    notification_type = request.data.get('type', 'email')
    message = request.data.get('message', '')
    
    if notification_type == 'email':
        notification = BookingNotification.objects.create(
            booking=booking,
            notification_type='email',
            sent_to=booking.email,
            subject=request.data.get('subject', 'Notification'),
            message=message
        )
    elif notification_type == 'whatsapp' and booking.agency.whatsapp:
        notification = BookingNotification.objects.create(
            booking=booking,
            notification_type='whatsapp',
            sent_to=booking.agency.whatsapp,
            message=message
        )
    else:
        return Response(
            {'error': 'Invalid notification type or missing WhatsApp number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = BookingNotificationSerializer(notification)
    return Response(serializer.data)
