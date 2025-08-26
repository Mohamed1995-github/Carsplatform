from django.db import models
from django.core.validators import RegexValidator
# from modeltranslation.translator import translator, TranslationOptions
from cars.models import Listing
from agencies.models import Agency


class Booking(models.Model):
    KIND_CHOICES = [
        ('rent', 'Location'),
        ('test_drive', 'Essai'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
        ('completed', 'Terminé'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings', verbose_name="Annonce")
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='bookings', verbose_name="Agence")
    
    # Booking type and status
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, verbose_name="Type de réservation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Customer information
    customer_name = models.CharField(max_length=200, verbose_name="Nom du client")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    
    # Dates
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    
    # For test drives
    test_drive_date = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure d'essai")
    
    # Additional information
    special_requests = models.TextField(blank=True, verbose_name="Demandes spéciales")
    
    # Pricing (for rentals)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix total")
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Montant de la caution")
    
    # Admin notes
    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Confirmé le")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Annulé le")
    
    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.listing} ({self.get_kind_display()})"
    
    @property
    def is_active(self):
        return self.status in ['pending', 'confirmed']
    
    @property
    def duration_days(self):
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 1
    
    def save(self, *args, **kwargs):
        # Auto-set agency from listing
        if not self.agency:
            self.agency = self.listing.car.agency
        
        # Auto-calculate total price for rentals
        if self.kind == 'rent' and self.listing.type == 'rent' and self.total_price is None:
            if self.listing.price_rent_daily:
                self.total_price = self.listing.price_rent_daily * self.duration_days
        
        super().save(*args, **kwargs)


class BookingNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications', verbose_name="Réservation")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Type de notification")
    sent_to = models.CharField(max_length=200, verbose_name="Envoyé à")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_sent = models.BooleanField(default=False, verbose_name="Envoyé")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyé le")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Notification de réservation"
        verbose_name_plural = "Notifications de réservation"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification {self.get_notification_type_display()} - {self.booking}"


# Translation configuration
# class BookingTranslationOptions(TranslationOptions):
#     fields = ('customer_name', 'special_requests')


# translator.register(Booking, BookingTranslationOptions)
