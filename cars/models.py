from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from modeltranslation.translator import translator, TranslationOptions
from agencies.models import Agency


class Car(models.Model):
    FUEL_CHOICES = [
        ('gasoline', 'Essence'),
        ('diesel', 'Diesel'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
        ('lpg', 'GPL'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manuelle'),
        ('automatic', 'Automatique'),
        ('semi_auto', 'Semi-automatique'),
    ]
    
    BODY_CHOICES = [
        ('sedan', 'Berline'),
        ('suv', 'SUV'),
        ('hatchback', 'Citadine'),
        ('wagon', 'Break'),
        ('coupe', 'Coupé'),
        ('convertible', 'Cabriolet'),
        ('van', 'Fourgon'),
        ('pickup', 'Pick-up'),
    ]
    
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='cars', verbose_name="Agence")
    
    # Basic car information
    make = models.CharField(max_length=100, verbose_name="Marque")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2030)],
        verbose_name="Année"
    )
    
    mileage = models.PositiveIntegerField(verbose_name="Kilométrage")
    
    fuel = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name="Carburant")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, verbose_name="Boîte de vitesse")
    body = models.CharField(max_length=20, choices=BODY_CHOICES, verbose_name="Carrosserie")
    
    # Engine and performance
    engine_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Cylindrée (L)")
    power = models.PositiveIntegerField(null=True, blank=True, verbose_name="Puissance (ch)")
    
    # Color
    color = models.CharField(max_length=50, verbose_name="Couleur")
    
    # Features and options
    features = models.JSONField(default=list, blank=True, verbose_name="Options")
    
    # Description
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Voiture"
        verbose_name_plural = "Voitures"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
    
    @property
    def cover_image(self):
        return self.images.filter(is_cover=True).first() or self.images.first()


class Listing(models.Model):
    TYPE_CHOICES = [
        ('sale', 'Vente'),
        ('rent', 'Location'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('paused', 'En pause'),
        ('sold', 'Vendu'),
        ('rented', 'Loué'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='listings', verbose_name="Voiture")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type d'annonce")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    
    # Pricing
    price_sale = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix de vente")
    price_rent_daily = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Prix location/jour")
    price_rent_weekly = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Prix location/semaine")
    price_rent_monthly = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Prix location/mois")
    
    # Visibility and SEO
    is_featured = models.BooleanField(default=False, verbose_name="Mis en avant")
    seo_title = models.CharField(max_length=200, blank=True, verbose_name="Titre SEO")
    seo_description = models.TextField(blank=True, verbose_name="Description SEO")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publié le")
    
    class Meta:
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"
        ordering = ['-created_at']
        unique_together = ['car', 'type']
    
    def __str__(self):
        return f"{self.car} - {self.get_type_display()}"
    
    @property
    def is_available(self):
        return self.status == 'published'
    
    @property
    def current_price(self):
        if self.type == 'sale':
            return self.price_sale
        return self.price_rent_daily


class RentalTerms(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='rental_terms', verbose_name="Annonce")
    
    # Rates
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Tarif journalier")
    weekly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Tarif hebdomadaire")
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Tarif mensuel")
    
    # Requirements
    deposit_required = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Caution requise")
    min_rental_days = models.PositiveIntegerField(default=1, verbose_name="Jours minimum de location")
    max_rental_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Jours maximum de location")
    
    # Pickup and return
    pickup_location = models.CharField(max_length=200, verbose_name="Lieu de retrait")
    return_location = models.CharField(max_length=200, blank=True, verbose_name="Lieu de retour")
    
    # Additional terms
    fuel_policy = models.CharField(max_length=50, default='full_to_full', verbose_name="Politique carburant")
    mileage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Limite kilométrage/jour")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Conditions de location"
        verbose_name_plural = "Conditions de location"
    
    def __str__(self):
        return f"Conditions de location - {self.listing}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images', verbose_name="Voiture")
    image = models.ImageField(upload_to='cars/images/', verbose_name="Image")
    is_cover = models.BooleanField(default=False, verbose_name="Image de couverture")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Ordre de tri")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texte alternatif")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Image de voiture"
        verbose_name_plural = "Images de voiture"
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"Image {self.sort_order} - {self.car}"
    
    def save(self, *args, **kwargs):
        if self.is_cover:
            # Ensure only one cover image per car
            CarImage.objects.filter(car=self.car, is_cover=True).update(is_cover=False)
        super().save(*args, **kwargs)


class Availability(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='availability', verbose_name="Voiture")
    date = models.DateField(verbose_name="Date")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    reason = models.CharField(max_length=200, blank=True, verbose_name="Raison de l'indisponibilité")
    
    class Meta:
        verbose_name = "Disponibilité"
        verbose_name_plural = "Disponibilités"
        unique_together = ['car', 'date']
        ordering = ['date']
    
    def __str__(self):
        status = "Disponible" if self.is_available else "Indisponible"
        return f"{self.car} - {self.date} ({status})"


# Translation configurations
# class CarTranslationOptions(TranslationOptions):
#     fields = ('make', 'model', 'color', 'description')


# class RentalTermsTranslationOptions(TranslationOptions):
#     fields = ('pickup_location', 'return_location')


# translator.register(Car, CarTranslationOptions)
# translator.register(RentalTerms, RentalTermsTranslationOptions)
