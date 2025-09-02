from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, UserProfile, OTP, UserSession
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('mobile', 'email', 'first_name', 'last_name')
    
    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get('mobile')
        email = cleaned_data.get('email')
        
        if not mobile and not email:
            raise ValidationError('Either mobile number or email must be provided.')
        
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    """Custom form for changing users"""
    class Meta(UserChangeForm.Meta):
        model = User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin interface for custom User model"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('get_identifier', 'username', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('mobile', 'email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'mobile', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def get_identifier(self, obj):
        return obj.get_identifier()
    get_identifier.short_description = 'Identifier'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ('user', 'first_name', 'last_name', 'city', 'state', 'country', 'created_at')
    list_filter = ('country', 'state', 'city', 'created_at')
    search_fields = ('user__mobile', 'user__email', 'user__username', 'first_name', 'last_name', 'city')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_picture')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin interface for OTP model"""
    list_display = ('user', 'otp_code', 'is_used', 'attempts', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__mobile', 'user__email', 'user__username', 'otp_code')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('OTP Details', {'fields': ('user', 'otp_code', 'is_used')}),
        ('Security', {'fields': ('attempts', 'max_attempts')}),
        ('Timestamps', {'fields': ('created_at', 'expires_at')}),
    )
    
    readonly_fields = ('created_at', 'expires_at')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession model"""
    list_display = ('user', 'session_key', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__mobile', 'user__email', 'user__username', 'session_key', 'ip_address')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Session', {'fields': ('user', 'session_key')}),
        ('Device Info', {'fields': ('ip_address', 'user_agent')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'last_activity'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'last_activity')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
