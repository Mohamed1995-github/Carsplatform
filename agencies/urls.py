from django.urls import path
from . import views

app_name = 'agencies'

urlpatterns = [
    path('agencies/', views.AgencyListView.as_view(), name='agency-list'),
    path('agencies/<int:pk>/', views.AgencyDetailView.as_view(), name='agency-detail'),
    path('agencies/register/', views.AgencyRegistrationView.as_view(), name='agency-register'),
    path('agencies/<int:pk>/verify/', views.AgencyVerificationView.as_view(), name='agency-verify'),
    path('agencies/<int:pk>/users/', views.AgencyUsersView.as_view(), name='agency-users'),
]

