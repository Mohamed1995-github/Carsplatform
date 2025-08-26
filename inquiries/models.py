from django.db import models
from django.core.validators import RegexValidator
# from modeltranslation.translator import translator, TranslationOptions
from cars.models import Listing
from agencies.models import Agency


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('closed', 'Fermé'),
        ('spam', 'Spam'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Site web'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Téléphone'),
        ('email', 'Email'),
        ('form', 'Formulaire de contact'),
    ]
    
    # Related objects
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries', verbose_name="Annonce", null=True, blank=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='inquiries', verbose_name="Agence")
    
    # Customer information
    customer_name = models.CharField(max_length=200, verbose_name="Nom du client")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    
    # Inquiry details
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    
    # Status and source
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Statut")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='form', verbose_name="Source")
    
    # Admin fields
    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ], default='medium', verbose_name="Priorité")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Lu le")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")
    
    class Meta:
        verbose_name = "Demande de renseignements"
        verbose_name_plural = "Demandes de renseignements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.subject}"
    
    @property
    def is_unread(self):
        return self.status == 'new'
    
    @property
    def is_urgent(self):
        return self.priority in ['high', 'urgent']
    
    def save(self, *args, **kwargs):
        # Auto-set agency from listing if not set
        if not self.agency and self.listing:
            self.agency = self.listing.car.agency
        
        # Update timestamps based on status changes
        if self.status == 'read' and not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
        elif self.status == 'replied' and not self.replied_at:
            from django.utils import timezone
            self.replied_at = timezone.now()
        
        super().save(*args, **kwargs)


class InquiryResponse(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='responses', verbose_name="Demande")
    response_text = models.TextField(verbose_name="Réponse")
    
    # Response details
    sent_by = models.CharField(max_length=100, verbose_name="Envoyé par")
    sent_via = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Téléphone'),
        ('sms', 'SMS'),
    ], verbose_name="Envoyé via")
    
    is_sent = models.BooleanField(default=False, verbose_name="Envoyé")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyé le")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Réponse à la demande"
        verbose_name_plural = "Réponses aux demandes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Réponse à {self.inquiry} - {self.sent_by}"


# Translation configuration
# class InquiryTranslationOptions(TranslationOptions):
#     fields = ('customer_name', 'subject', 'message')


# class InquiryResponseTranslationOptions(TranslationOptions):
#     fields = ('response_text',)


# translator.register(Inquiry, InquiryTranslationOptions)
# translator.register(InquiryResponse, InquiryResponseTranslationOptions)
