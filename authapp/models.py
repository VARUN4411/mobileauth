from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
import secrets
import string


class UserManager(BaseUserManager):
    def create_user(self, mobile=None, email=None, password=None, **extra_fields):
        if not mobile and not email:
            raise ValueError("Either mobile or email must be set")

        username = extra_fields.get('username')
        if not username:
            if mobile:
                username = f"user_{mobile.replace('+','')}"
            elif email:
                username = f"user_{email.split('@')[0]}"
            extra_fields['username'] = username

        # Generate password if not provided
        if not password:
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user = self.model(mobile=mobile, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile, email, password, **extra_fields)
class User(AbstractUser):
    """Custom User model for OTP-based authentication"""
    # Keep username field but make it optional
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text='Username (optional, can be left blank)'
    )
    
    # Primary identifier - mobile number or email
    mobile = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Mobile number must be entered in the format: +999999999. Up to 15 digits allowed.'
            )
        ],
        help_text='Mobile number (e.g., +1234567890)'
    )
    
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text='Email address'
    )
    objects = UserManager()
    # Ensure at least one identifier is provided
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.mobile and not self.email:
            raise ValidationError('Either mobile number or email must be provided.')
    
    def save(self, *args, **kwargs):
        # Generate username if not provided
        if not self.username:
            if self.mobile:
                self.username = f"user_{self.mobile.replace('+', '').replace('-', '')}"
            elif self.email:
                self.username = f"user_{self.email.split('@')[0]}"
        
        self.clean()
        super().save(*args, **kwargs)
    
    # Use mobile as primary identifier, fallback to email
    def get_identifier(self):
        return self.mobile or self.email
    
    def __str__(self):
        identifier = self.get_identifier()
        return f"User({identifier})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Basic information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Address information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    
    # Additional fields
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"Profile for {self.user.get_identifier()}"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class OTP(models.Model):
    """One-Time Password for authentication"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    
    # OTP details
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Rate limiting
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired() and self.attempts < self.max_attempts
    
    def increment_attempts(self):
        self.attempts += 1
        self.save()
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
    
    def __str__(self):
        return f"OTP for {self.user.get_identifier()} - {self.otp_code}"
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']

class UserSession(models.Model):
    """User session management for security"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Security
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session for {self.user.get_identifier()}"
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
