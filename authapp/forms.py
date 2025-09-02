from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserProfile
from .utils import is_valid_mobile, is_valid_email

class LoginForm(forms.Form):
    """Form for initial login with mobile/email"""
    identifier = forms.CharField(
        label='Mobile Number or Email',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter mobile number or email',
            'autocomplete': 'off'
        })
    )
    
    def clean_identifier(self):
        identifier = self.cleaned_data['identifier'].strip()
        
        if not identifier:
            raise ValidationError('Please enter mobile number or email')
        
        # Validate format
        if '@' in identifier:
            if not is_valid_email(identifier):
                raise ValidationError('Please enter a valid email address')
        else:
            if not is_valid_mobile(identifier):
                raise ValidationError('Please enter a valid mobile number')
        
        return identifier

class OTPVerificationForm(forms.Form):
    """Form for OTP verification"""
    otp_code = forms.CharField(
        label='OTP Code',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autocomplete': 'off',
            'maxlength': '6'
        })
    )
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data['otp_code'].strip()
        
        if not otp_code.isdigit():
            raise ValidationError('OTP must contain only digits')
        
        if len(otp_code) != 6:
            raise ValidationError('OTP must be exactly 6 digits')
        
        return otp_code

class ProfileCompletionForm(forms.ModelForm):
    """Form for completing user profile after first login"""
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'date_of_birth'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 1'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 2 (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure required fields are filled
        required_fields = ['first_name', 'last_name', 'address_line1', 'city', 'state', 'postal_code']
        for field in required_fields:
            if not cleaned_data.get(field):
                raise ValidationError(f'{field.replace("_", " ").title()} is required')
        
        return cleaned_data

class ResendOTPForm(forms.Form):
    """Form for resending OTP"""
    identifier = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_identifier(self):
        identifier = self.cleaned_data['identifier']
        
        if not identifier:
            raise ValidationError('Identifier is required')
        
        return identifier

