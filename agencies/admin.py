from django.contrib import admin
from django.utils.html import format_html
from .models import Agency, AgencyUser


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'status', 'is_verified', 'created_at']
    list_filter = ['status', 'is_verified', 'city', 'created_at']
    search_fields = ['name', 'city', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'verification_date']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'name_ar', 'city', 'city_ar', 'address', 'address_ar')
        }),
        ('Contact', {
            'fields': ('phone', 'whatsapp', 'email', 'website')
        }),
        ('Vérification', {
            'fields': ('status', 'is_verified', 'verification_date', 'kbis_rc')
        }),
        ('Description', {
            'fields': ('description', 'description_ar'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_agencies', 'reject_agencies', 'mark_as_verified']
    
    def approve_agencies(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='approved', verification_date=timezone.now())
        self.message_user(request, f'{updated} agence(s) approuvée(s).')
    approve_agencies.short_description = "Approuver les agences sélectionnées"
    
    def reject_agencies(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} agence(s) rejetée(s).')
    reject_agencies.short_description = "Rejeter les agences sélectionnées"
    
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f'{updated} agence(s) marquée(s) comme vérifiée(s).')
    mark_as_verified.short_description = "Marquer comme vérifiées"


@admin.register(AgencyUser)
class AgencyUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'agency', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'agency', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'agency__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'agency', 'role')
        }),
        ('Informations supplémentaires', {
            'fields': ('phone', 'position', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} utilisateur(s) activé(s).')
    activate_users.short_description = "Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} utilisateur(s) désactivé(s).')
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"
