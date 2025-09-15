from django.contrib import admin
from .models import Booking, BookingNotification


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'listing', 'kind', 'status', 'start_date', 'end_date', 'total_price', 'created_at']
    list_filter = ['kind', 'status', 'agency', 'created_at', 'start_date']
    search_fields = ['customer_name', 'phone', 'email', 'listing__car__make', 'listing__car__model']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'cancelled_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Réservation', {
            'fields': ('listing', 'agency', 'kind', 'status')
        }),
        ('Client', {
            'fields': ('customer_name', 'phone', 'email')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'test_drive_date')
        }),
        ('Prix et caution', {
            'fields': ('total_price', 'deposit_amount')
        }),
        ('Demandes spéciales', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Notes administrateur', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_completed']
    
    def confirm_bookings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f'{updated} réservation(s) confirmée(s).')
    confirm_bookings.short_description = "Confirmer les réservations sélectionnées"
    
    def cancel_bookings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='cancelled', cancelled_at=timezone.now())
        self.message_user(request, f'{updated} réservation(s) annulée(s).')
    cancel_bookings.short_description = "Annuler les réservations sélectionnées"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} réservation(s) marquée(s) comme terminée(s).')
    mark_as_completed.short_description = "Marquer comme terminées"


@admin.register(BookingNotification)
class BookingNotificationAdmin(admin.ModelAdmin):
    list_display = ['booking', 'notification_type', 'sent_to', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'is_sent', 'created_at']
    search_fields = ['booking__customer_name', 'sent_to', 'subject']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Réservation', {
            'fields': ('booking',)
        }),
        ('Notification', {
            'fields': ('notification_type', 'sent_to', 'subject', 'message')
        }),
        ('Statut', {
            'fields': ('is_sent', 'sent_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_unsent']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} notification(s) marquée(s) comme envoyée(s).')
    mark_as_sent.short_description = "Marquer comme envoyées"
    
    def mark_as_unsent(self, request, queryset):
        updated = queryset.update(is_sent=False, sent_at=None)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme non envoyée(s).')
    mark_as_unsent.short_description = "Marquer comme non envoyées"
