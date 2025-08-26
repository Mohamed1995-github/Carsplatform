from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    # Car listings
    path('cars/', views.CarListView.as_view(), name='car-list'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car-detail'),
    path('cars/<int:pk>/images/', views.CarImagesView.as_view(), name='car-images'),
    
    # Listings
    path('listings/', views.ListingListView.as_view(), name='listing-list'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('listings/search/', views.ListingSearchView.as_view(), name='listing-search'),
    path('listings/featured/', views.FeaturedListingsView.as_view(), name='featured-listings'),
    
    # Availability
    path('cars/<int:pk>/availability/', views.CarAvailabilityView.as_view(), name='car-availability'),
    path('cars/<int:pk>/availability/<str:date>/', views.CarAvailabilityDetailView.as_view(), name='car-availability-detail'),
    
    # Agency-specific endpoints
    path('agencies/<int:agency_id>/cars/', views.AgencyCarsView.as_view(), name='agency-cars'),
    path('agencies/<int:agency_id>/listings/', views.AgencyListingsView.as_view(), name='agency-listings'),
]

