from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# from modeltranslation.translator import translator, TranslationOptions


class Agency(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('suspended', 'Suspendu'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom de l'agence")
    city = models.CharField(max_length=100, verbose_name="Ville")
    address = models.TextField(verbose_name="Adresse")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Téléphone")
    
    whatsapp = models.CharField(validators=[phone_regex], max_length=17, verbose_name="WhatsApp", blank=True)
    
    email = models.EmailField(verbose_name="Email")
    
    # Verification documents
    kbis_rc = models.FileField(upload_to='agencies/documents/', verbose_name="K-bis/RC", blank=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    verification_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de vérification")
    
    # Additional info
    description = models.TextField(blank=True, verbose_name="Description")
    
    website = models.URLField(blank=True, verbose_name="Site web")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'approved' and self.is_verified


class AgencyUser(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Propriétaire'),
        ('staff', 'Employé'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='users', verbose_name="Agence")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff', verbose_name="Rôle")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Additional fields
    phone = models.CharField(max_length=17, blank=True, verbose_name="Téléphone")
    position = models.CharField(max_length=100, blank=True, verbose_name="Poste")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Utilisateur d'agence"
        verbose_name_plural = "Utilisateurs d'agence"
        unique_together = ['user', 'agency']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.agency.name} ({self.get_role_display()})"
    
    @property
    def is_owner(self):
        return self.role == 'owner'


# Translation configuration
# class AgencyTranslationOptions(TranslationOptions):
#     fields = ('name', 'city', 'address', 'description')


# translator.register(Agency, AgencyTranslationOptions)
