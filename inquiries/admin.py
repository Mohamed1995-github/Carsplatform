from django.contrib import admin
from .models import Inquiry, InquiryResponse


class InquiryResponseInline(admin.TabularInline):
    model = InquiryResponse
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'subject', 'agency', 'status', 'priority', 'source', 'created_at']
    list_filter = ['status', 'priority', 'source', 'agency', 'created_at']
    search_fields = ['customer_name', 'subject', 'phone', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at', 'read_at', 'replied_at']
    date_hierarchy = 'created_at'
    inlines = [InquiryResponseInline]
    
    fieldsets = (
        ('Demande', {
            'fields': ('listing', 'agency', 'status', 'priority', 'source')
        }),
        ('Client', {
            'fields': ('customer_name', 'phone', 'email')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Notes administrateur', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at', 'replied_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_closed', 'mark_as_spam']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='read', read_at=timezone.now())
        self.message_user(request, f'{updated} demande(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = "Marquer comme lues"
    
    def mark_as_replied(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='replied', replied_at=timezone.now())
        self.message_user(request, f'{updated} demande(s) marquée(s) comme répondue(s).')
    mark_as_replied.short_description = "Marquer comme répondues"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} demande(s) marquée(s) comme fermée(s).')
    mark_as_closed.short_description = "Marquer comme fermées"
    
    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='spam')
        self.message_user(request, f'{updated} demande(s) marquée(s) comme spam.')
    mark_as_spam.short_description = "Marquer comme spam"


@admin.register(InquiryResponse)
class InquiryResponseAdmin(admin.ModelAdmin):
    list_display = ['inquiry', 'sent_by', 'sent_via', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['sent_via', 'is_sent', 'created_at']
    search_fields = ['inquiry__customer_name', 'inquiry__subject', 'sent_by']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Demande', {
            'fields': ('inquiry',)
        }),
        ('Réponse', {
            'fields': ('response_text',)
        }),
        ('Envoi', {
            'fields': ('sent_by', 'sent_via', 'is_sent', 'sent_at', 'error_message')
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
        self.message_user(request, f'{updated} réponse(s) marquée(s) comme envoyée(s).')
    mark_as_sent.short_description = "Marquer comme envoyées"
    
    def mark_as_unsent(self, request, queryset):
        updated = queryset.update(is_sent=False, sent_at=None)
        self.message_user(request, f'{updated} réponse(s) marquée(s) comme non envoyée(s).')
    mark_as_unsent.short_description = "Marquer comme non envoyées"
