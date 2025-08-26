from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Inquiry, InquiryResponse
from .serializers import (
    InquirySerializer, InquiryCreateSerializer, InquiryResponseSerializer,
    ContactFormSerializer
)
from datetime import date


class InquiryListView(generics.ListAPIView):
    """List all inquiries (admin only)"""
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['-created_at']


class InquiryDetailView(generics.RetrieveAPIView):
    """Get inquiry details"""
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]


class InquiryCreateView(generics.CreateAPIView):
    """Create a new inquiry"""
    serializer_class = InquiryCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        inquiry = serializer.save()
        
        # Create notification for agency
        InquiryResponse.objects.create(
            inquiry=inquiry,
            response_text=f"Nouvelle demande de renseignements reçue de {inquiry.customer_name}",
            sent_by="Système",
            sent_via="email"
        )


class InquiryReplyView(generics.CreateAPIView):
    """Reply to an inquiry"""
    serializer_class = InquiryResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        inquiry_id = self.kwargs.get('pk')
        inquiry = get_object_or_404(Inquiry, id=inquiry_id)
        
        response = serializer.save(inquiry=inquiry)
        
        # Update inquiry status
        inquiry.status = 'replied'
        inquiry.replied_at = timezone.now()
        inquiry.save()
        
        return response


class AgencyInquiriesView(generics.ListAPIView):
    """Get inquiries for a specific agency"""
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_id')
        return Inquiry.objects.filter(agency_id=agency_id).order_by('-created_at')


class ContactFormView(generics.CreateAPIView):
    """Handle contact form submissions"""
    serializer_class = ContactFormSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        inquiry = serializer.save()
        
        # Create notification for agency
        InquiryResponse.objects.create(
            inquiry=inquiry,
            response_text=f"Message de contact reçu de {inquiry.customer_name}",
            sent_by="Système",
            sent_via="email"
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inquiry_stats(request, agency_id):
    """Get inquiry statistics for an agency"""
    from django.db.models import Count, Q
    from datetime import timedelta
    
    # Get date range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get inquiries for the agency
    inquiries = Inquiry.objects.filter(agency_id=agency_id)
    
    stats = {
        'total_inquiries': inquiries.count(),
        'new_inquiries': inquiries.filter(status='new').count(),
        'read_inquiries': inquiries.filter(status='read').count(),
        'replied_inquiries': inquiries.filter(status='replied').count(),
        'closed_inquiries': inquiries.filter(status='closed').count(),
        'spam_inquiries': inquiries.filter(status='spam').count(),
        'recent_inquiries': inquiries.filter(created_at__date__gte=start_date).count(),
        'urgent_inquiries': inquiries.filter(priority__in=['high', 'urgent']).count(),
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_inquiry_read(request, pk):
    """Mark an inquiry as read"""
    inquiry = get_object_or_404(Inquiry, id=pk)
    inquiry.status = 'read'
    inquiry.read_at = timezone.now()
    inquiry.save()
    
    serializer = InquirySerializer(inquiry)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_inquiry_spam(request, pk):
    """Mark an inquiry as spam"""
    inquiry = get_object_or_404(Inquiry, id=pk)
    inquiry.status = 'spam'
    inquiry.save()
    
    serializer = InquirySerializer(inquiry)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def close_inquiry(request, pk):
    """Close an inquiry"""
    inquiry = get_object_or_404(Inquiry, id=pk)
    inquiry.status = 'closed'
    inquiry.save()
    
    serializer = InquirySerializer(inquiry)
    return Response(serializer.data)
