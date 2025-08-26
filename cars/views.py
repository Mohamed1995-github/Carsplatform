from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, date
from .models import Car, Listing, CarImage, Availability
from .serializers import (
    CarSerializer, ListingSerializer, CarImageSerializer, 
    AvailabilitySerializer, ListingSearchSerializer
)


class CarListView(generics.ListAPIView):
    """List all cars with filtering"""
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['make', 'fuel', 'transmission', 'body', 'agency']
    search_fields = ['make', 'model', 'agency__name', 'agency__city']
    ordering_fields = ['year', 'mileage', 'created_at']
    ordering = ['-created_at']


class CarDetailView(generics.RetrieveAPIView):
    """Get car details"""
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.AllowAny]


class CarImagesView(generics.ListAPIView):
    """Get car images"""
    serializer_class = CarImageSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        car_id = self.kwargs.get('pk')
        return CarImage.objects.filter(car_id=car_id).order_by('sort_order')


class ListingListView(generics.ListAPIView):
    """List all published listings"""
    queryset = Listing.objects.filter(status='published')
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'car__make', 'car__fuel', 'car__transmission', 'car__agency']
    search_fields = ['car__make', 'car__model', 'car__agency__name', 'car__agency__city']
    ordering_fields = ['price_sale', 'price_rent_daily', 'created_at']
    ordering = ['-created_at']


class ListingDetailView(generics.RetrieveAPIView):
    """Get listing details"""
    queryset = Listing.objects.filter(status='published')
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]


class ListingSearchView(generics.ListAPIView):
    """Advanced search for listings"""
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Listing.objects.filter(status='published')
        
        # Get search parameters
        make = self.request.query_params.get('make')
        model = self.request.query_params.get('model')
        year_min = self.request.query_params.get('year_min')
        year_max = self.request.query_params.get('year_max')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        mileage_max = self.request.query_params.get('mileage_max')
        fuel = self.request.query_params.get('fuel')
        transmission = self.request.query_params.get('transmission')
        city = self.request.query_params.get('city')
        listing_type = self.request.query_params.get('type')
        
        # Apply filters
        if make:
            queryset = queryset.filter(car__make__icontains=make)
        if model:
            queryset = queryset.filter(car__model__icontains=model)
        if year_min:
            queryset = queryset.filter(car__year__gte=year_min)
        if year_max:
            queryset = queryset.filter(car__year__lte=year_max)
        if mileage_max:
            queryset = queryset.filter(car__mileage__lte=mileage_max)
        if fuel:
            queryset = queryset.filter(car__fuel=fuel)
        if transmission:
            queryset = queryset.filter(car__transmission=transmission)
        if city:
            queryset = queryset.filter(car__agency__city__icontains=city)
        if listing_type:
            queryset = queryset.filter(type=listing_type)
        
        # Price filtering based on listing type
        if listing_type == 'sale' or not listing_type:
            if price_min:
                queryset = queryset.filter(price_sale__gte=price_min)
            if price_max:
                queryset = queryset.filter(price_sale__lte=price_max)
        elif listing_type == 'rent':
            if price_min:
                queryset = queryset.filter(price_rent_daily__gte=price_min)
            if price_max:
                queryset = queryset.filter(price_rent_daily__lte=price_max)
        
        return queryset


class FeaturedListingsView(generics.ListAPIView):
    """Get featured listings"""
    queryset = Listing.objects.filter(status='published', is_featured=True)
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['-created_at']


class CarAvailabilityView(generics.ListCreateAPIView):
    """Get and manage car availability"""
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        car_id = self.kwargs.get('pk')
        return Availability.objects.filter(car_id=car_id)
    
    def perform_create(self, serializer):
        car_id = self.kwargs.get('pk')
        serializer.save(car_id=car_id)


class CarAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete specific availability"""
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        car_id = self.kwargs.get('pk')
        date_str = self.kwargs.get('date')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        return get_object_or_404(Availability, car_id=car_id, date=date_obj)


class AgencyCarsView(generics.ListAPIView):
    """Get cars for a specific agency"""
    serializer_class = CarSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_id')
        return Car.objects.filter(agency_id=agency_id)


class AgencyListingsView(generics.ListAPIView):
    """Get listings for a specific agency"""
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        agency_id = self.kwargs.get('agency_id')
        return Listing.objects.filter(car__agency_id=agency_id, status='published')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def car_makes(request):
    """Get all car makes"""
    makes = Car.objects.values_list('make', flat=True).distinct().order_by('make')
    return Response(list(makes))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def car_models(request, make):
    """Get models for a specific make"""
    models = Car.objects.filter(make=make).values_list('model', flat=True).distinct().order_by('model')
    return Response(list(models))
