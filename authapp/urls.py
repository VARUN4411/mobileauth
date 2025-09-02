from django.urls import path
from . import views

app_name = 'authapp'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('otp-verification/', views.otp_verification_view, name='otp_verification'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile-completion/', views.profile_completion_view, name='profile_completion'),
    path('profile/', views.profile_view, name='profile'),
    
    # Home URL
    path('', views.home_view, name='home'),
    
    # API URLs
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
]

