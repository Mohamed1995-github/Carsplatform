from django.urls import path
from . import views

app_name = 'inquiries'

urlpatterns = [
    # Inquiries
    path('inquiries/', views.InquiryListView.as_view(), name='inquiry-list'),
    path('inquiries/<int:pk>/', views.InquiryDetailView.as_view(), name='inquiry-detail'),
    path('inquiries/create/', views.InquiryCreateView.as_view(), name='inquiry-create'),
    path('inquiries/<int:pk>/reply/', views.InquiryReplyView.as_view(), name='inquiry-reply'),
    
    # Agency inquiries
    path('agencies/<int:agency_id>/inquiries/', views.AgencyInquiriesView.as_view(), name='agency-inquiries'),
    
    # Contact form
    path('contact/', views.ContactFormView.as_view(), name='contact-form'),
]
