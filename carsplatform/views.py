from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from cars.models import Car, Listing
from agencies.models import Agency
from bookings.models import Booking


def home(request):
    """Page d'accueil avec statistiques et voitures en vedette"""
    context = {
        'featured_listings': Listing.objects.filter(
            status='published', 
            is_featured=True
        ).select_related('car', 'car__agency')[:6],
        'total_cars': Car.objects.count(),
        'total_agencies': Agency.objects.filter(status='approved').count(),
        'total_listings': Listing.objects.filter(status='published').count(),
        'total_bookings': Booking.objects.count(),
    }
    return render(request, 'home.html', context)


def car_list(request):
    """Liste des voitures avec filtres"""
    cars = Car.objects.select_related('agency').prefetch_related('images')
    
    # Filtres
    make = request.GET.get('make')
    if make:
        cars = cars.filter(make__icontains=make)
    
    fuel = request.GET.get('fuel')
    if fuel:
        cars = cars.filter(fuel=fuel)
    
    transmission = request.GET.get('transmission')
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    year_min = request.GET.get('year_min')
    if year_min:
        cars = cars.filter(year__gte=year_min)
    
    year_max = request.GET.get('year_max')
    if year_max:
        cars = cars.filter(year__lte=year_max)
    
    # Tri
    cars = cars.order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(cars, 12)  # 12 voitures par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cars/list.html', {'page_obj': page_obj})


def car_detail(request, pk):
    """Détails d'une voiture"""
    car = Car.objects.select_related('agency').prefetch_related('images', 'listings').get(pk=pk)
    return render(request, 'cars/detail.html', {'car': car})


def listing_list(request):
    """Liste des annonces"""
    listings = Listing.objects.filter(status='published').select_related('car', 'car__agency')
    return render(request, 'cars/listing_list.html', {'listings': listings})


def listing_detail(request, pk):
    """Détails d'une annonce"""
    listing = Listing.objects.select_related('car', 'car__agency').get(pk=pk)
    return render(request, 'cars/listing_detail.html', {'listing': listing})


def listing_search(request):
    """Recherche avancée d'annonces"""
    listings = Listing.objects.filter(status='published').select_related('car', 'car__agency')
    
    # Appliquer les filtres de recherche
    make = request.GET.get('make')
    if make:
        listings = listings.filter(car__make__icontains=make)
    
    model = request.GET.get('model')
    if model:
        listings = listings.filter(car__model__icontains=model)
    
    listing_type = request.GET.get('type')
    if listing_type:
        listings = listings.filter(type=listing_type)
    
    price_max = request.GET.get('price_max')
    if price_max:
        listings = listings.filter(price_sale__lte=price_max)
    
    return render(request, 'cars/search_results.html', {'listings': listings})


def agency_list(request):
    """Liste des agences"""
    agencies = Agency.objects.filter(status='approved')
    return render(request, 'agencies/list.html', {'agencies': agencies})


def agency_detail(request, pk):
    """Détails d'une agence"""
    agency = Agency.objects.get(pk=pk)
    return render(request, 'agencies/detail.html', {'agency': agency})


def agency_register(request):
    """Inscription d'une agence"""
    return render(request, 'agencies/register.html')


def contact(request):
    """Page de contact"""
    return render(request, 'contact.html')


def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('home')



