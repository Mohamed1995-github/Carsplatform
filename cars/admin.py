from django.contrib import admin
from django.utils.html import format_html
from .models import Car, Listing, RentalTerms, CarImage, Availability


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ['image', 'is_cover', 'sort_order', 'alt_text']


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1
    fields = ['date', 'is_available', 'reason']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'agency', 'fuel', 'transmission', 'mileage', 'created_at']
    list_filter = ['make', 'fuel', 'transmission', 'body', 'year', 'agency', 'created_at']
    search_fields = ['make', 'model', 'agency__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CarImageInline, AvailabilityInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('agency', 'make', 'model', 'year', 'mileage')
        }),
        ('Spécifications techniques', {
            'fields': ('fuel', 'transmission', 'body', 'engine_size', 'power')
        }),
        ('Apparence', {
            'fields': ('color',)
        }),
        ('Options et description', {
            'fields': ('features', 'description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class RentalTermsInline(admin.StackedInline):
    model = RentalTerms
    extra = 0


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['car', 'type', 'status', 'current_price', 'is_featured', 'created_at']
    list_filter = ['type', 'status', 'is_featured', 'car__agency', 'created_at']
    search_fields = ['car__make', 'car__model', 'car__agency__name']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    inlines = [RentalTermsInline]
    
    fieldsets = (
        ('Voiture et type', {
            'fields': ('car', 'type', 'status')
        }),
        ('Prix', {
            'fields': ('price_sale', 'price_rent_daily', 'price_rent_weekly', 'price_rent_monthly')
        }),
        ('Visibilité et SEO', {
            'fields': ('is_featured', 'seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_listings', 'pause_listings', 'mark_as_featured']
    
    def publish_listings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} annonce(s) publiée(s).')
    publish_listings.short_description = "Publier les annonces sélectionnées"
    
    def pause_listings(self, request, queryset):
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} annonce(s) mise(s) en pause.')
    pause_listings.short_description = "Mettre en pause les annonces sélectionnées"
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} annonce(s) mise(s) en avant.')
    mark_as_featured.short_description = "Mettre en avant les annonces sélectionnées"


@admin.register(RentalTerms)
class RentalTermsAdmin(admin.ModelAdmin):
    list_display = ['listing', 'daily_rate', 'weekly_rate', 'monthly_rate', 'deposit_required']
    list_filter = ['listing__type', 'listing__car__agency']
    search_fields = ['listing__car__make', 'listing__car__model']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Annonce', {
            'fields': ('listing',)
        }),
        ('Tarifs', {
            'fields': ('daily_rate', 'weekly_rate', 'monthly_rate')
        }),
        ('Conditions', {
            'fields': ('deposit_required', 'min_rental_days', 'max_rental_days')
        }),
        ('Lieux', {
            'fields': ('pickup_location', 'return_location')
        }),
        ('Politiques', {
            'fields': ('fuel_policy', 'mileage_limit'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'image_preview', 'is_cover', 'sort_order', 'created_at']
    list_filter = ['is_cover', 'car__agency', 'created_at']
    search_fields = ['car__make', 'car__model']
    readonly_fields = ['created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"
    
    fieldsets = (
        ('Voiture', {
            'fields': ('car',)
        }),
        ('Image', {
            'fields': ('image', 'is_cover', 'sort_order', 'alt_text')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['car', 'date', 'is_available', 'reason']
    list_filter = ['is_available', 'car__agency', 'date']
    search_fields = ['car__make', 'car__model', 'reason']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Voiture', {
            'fields': ('car',)
        }),
        ('Disponibilité', {
            'fields': ('date', 'is_available', 'reason')
        }),
    )
