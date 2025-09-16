from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Agency, AgencyUser
from .serializers import AgencySerializer, AgencyUserSerializer, AgencyRegistrationSerializer


class AgencyListView(generics.ListAPIView):
    """List all approved agencies"""
    queryset = Agency.objects.filter(status='approved', is_verified=True)
    serializer_class = AgencySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset


class AgencyDetailView(generics.RetrieveAPIView):
    """Get agency details"""
    queryset = Agency.objects.filter(status='approved', is_verified=True)
    serializer_class = AgencySerializer
    permission_classes = [permissions.AllowAny]


class AgencyRegistrationView(generics.CreateAPIView):
    """Register a new agency"""
    serializer_class = AgencyRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        agency = serializer.save()
        
        # Create user account for agency owner
        user_data = self.request.data.get('user', {})
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create agency user relationship
        AgencyUser.objects.create(
            user=user,
            agency=agency,
            role='owner',
            phone=user_data.get('phone', ''),
            position=user_data.get('position', 'Propriétaire')
        )


class AgencyVerificationView(generics.UpdateAPIView):
    """Verify an agency (admin only)"""
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        agency = self.get_object()
        agency.status = 'approved'
        agency.is_verified = True
        agency.verification_date = timezone.now()
        agency.save()
        
        serializer = self.get_serializer(agency)
        return Response(serializer.data)


class AgencyUsersView(generics.ListCreateAPIView):
    """List and create agency users"""
    serializer_class = AgencyUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('pk')
        return AgencyUser.objects.filter(agency_id=agency_id)
    
    def perform_create(self, serializer):
        agency_id = self.kwargs.get('pk')
        serializer.save(agency_id=agency_id)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def agency_stats(request, pk):
    """Get agency statistics"""
    agency = get_object_or_404(Agency, pk=pk)
    
    stats = {
        'total_cars': agency.cars.count(),
        'active_listings': agency.cars.filter(listings__status='published').distinct().count(),
        'total_bookings': agency.bookings.count(),
        'pending_bookings': agency.bookings.filter(status='pending').count(),
        'total_inquiries': agency.inquiries.count(),
        'unread_inquiries': agency.inquiries.filter(status='new').count(),
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def agency_whatsapp_redirect(request, pk):
    """Redirect to the agency WhatsApp wa.me link with prefilled message."""
    agency = get_object_or_404(Agency, pk=pk)
    # Build link similarly to serializer method to keep behavior consistent
    from urllib.parse import quote
    import re

    if not agency.whatsapp:
        return Response({"detail": "WhatsApp non disponible pour cette agence."}, status=status.HTTP_404_NOT_FOUND)

    digits_only = re.sub(r"\D", "", agency.whatsapp)
    if not digits_only:
        return Response({"detail": "Numéro WhatsApp invalide."}, status=status.HTTP_400_BAD_REQUEST)

    message = f"Bonjour {agency.name}, je souhaite vous contacter via AutoPlatform."
    url = f"https://wa.me/{digits_only}?text={quote(message, safe='')}"
    return HttpResponseRedirect(url)
