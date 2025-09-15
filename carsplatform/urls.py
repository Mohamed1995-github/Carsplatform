"""
URL configuration for carsplatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from . import views


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint that provides links to all available endpoints.
    """
    return Response({
        'agencies': '/api/agencies/',
        'cars': '/api/cars/',
        'listings': '/api/listings/',
        'bookings': '/api/bookings/',
        'inquiries': '/api/inquiries/',
        'contact': '/api/contact/',
        'admin': '/admin/',
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pages principales
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/search/', views.listing_search, name='listing_search'),
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/<int:pk>/', views.agency_detail, name='agency_detail'),
    path('agencies/register/', views.agency_register, name='agency_register'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    
    # API
    path('api/', api_root, name='api-root'),
    path('api/', include('agencies.urls')),
    path('api/', include('cars.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('inquiries.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Administration - Plateforme Voitures"
admin.site.site_title = "Admin Voitures"
admin.site.index_title = "Bienvenue dans l'administration"
