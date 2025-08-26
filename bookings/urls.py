from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Bookings
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:pk>/confirm/', views.BookingConfirmView.as_view(), name='booking-confirm'),
    path('bookings/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking-cancel'),
    
    # Agency bookings
    path('agencies/<int:agency_id>/bookings/', views.AgencyBookingsView.as_view(), name='agency-bookings'),
    
    # Notifications
    path('bookings/<int:booking_id>/notifications/', views.BookingNotificationsView.as_view(), name='booking-notifications'),
]

