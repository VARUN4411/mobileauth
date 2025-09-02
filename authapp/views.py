from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import logging

from .models import User, UserProfile, OTP, UserSession
from .forms import LoginForm, OTPVerificationForm, ProfileCompletionForm, ResendOTPForm
from .utils import (
    generate_otp, send_otp, create_otp_instance, 
    get_identifier_type, cleanup_expired_otps
)

logger = logging.getLogger(__name__)

def login_view(request):
    """Initial login view - collect mobile/email"""
    if request.user.is_authenticated:
        return redirect('authapp:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            
            try:
                # Check if user exists
                if '@' in identifier:
                    user = User.objects.get(email=identifier)
                else:
                    user = User.objects.get(mobile=identifier)
                
                # Generate and send OTP
                otp_code = generate_otp(settings.OTP_LENGTH)
                otp_instance = create_otp_instance(user, otp_code)
                
                # Send OTP
                if send_otp(identifier, otp_code):
                    # Store identifier in session for OTP verification
                    request.session['login_identifier'] = identifier
                    request.session['user_id'] = user.id
                    
                    messages.success(request, f'OTP sent to {identifier}')
                    return redirect('authapp:otp_verification')
                else:
                    messages.error(request, 'Failed to send OTP. Please try again.')
                    otp_instance.delete()  # Clean up failed OTP
                    
            except User.DoesNotExist:
                # Create new user
                if '@' in identifier:
                    user = User.objects.create_user(
                        email=identifier,
                        mobile=None
                    )
                else:
                    user = User.objects.create_user(
                        mobile=identifier,
                        email=None
                    )
                
                # Generate and send OTP for new user
                otp_code = generate_otp(settings.OTP_LENGTH)
                otp_instance = create_otp_instance(user, otp_code)
                
                if send_otp(identifier, otp_code):
                    request.session['login_identifier'] = identifier
                    request.session['user_id'] = user.id
                    request.session['is_new_user'] = True
                    
                    messages.success(request, f'OTP sent to {identifier}')
                    return redirect('authapp:otp_verification')
                else:
                    messages.error(request, 'Failed to send OTP. Please try again.')
                    otp_instance.delete()
                    user.delete()  # Clean up failed user creation
    else:
        form = LoginForm()
    
    return render(request, 'authapp/login.html', {'form': form})

def otp_verification_view(request):
    """OTP verification view"""
    if request.user.is_authenticated:
        return redirect('authapp:home')
    
    # Check if we have the required session data
    identifier = request.session.get('login_identifier')
    user_id = request.session.get('user_id')
    
    if not identifier or not user_id:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            
            # Find valid OTP
            try:
                otp_instance = OTP.objects.get(
                    user=user,
                    otp_code=otp_code,
                    is_used=False,
                    expires_at__gt=timezone.now()
                )
                
                # Check attempts
                if otp_instance.attempts >= otp_instance.max_attempts:
                    messages.error(request, 'OTP attempts exceeded. Please request a new OTP.')
                    return redirect('login')
                
                # Mark OTP as used
                otp_instance.mark_as_used()
                
                # Login user
                login(request, user)
                
                # Create session record
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Check if user needs to complete profile
                if request.session.get('is_new_user') or not hasattr(user, 'profile'):
                    messages.success(request, 'Welcome! Please complete your profile.')
                    return redirect('authapp:profile_completion')
                else:
                    messages.success(request, f'Welcome back, {user.profile.first_name}!')
                    return redirect('authapp:home')
                    
            except OTP.DoesNotExist:
                # Increment attempts for existing OTP
                try:
                    existing_otp = OTP.objects.get(
                        user=user,
                        otp_code=otp_code,
                        is_used=False
                    )
                    existing_otp.increment_attempts()
                except OTP.DoesNotExist:
                    pass
                
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
     # Clean up expired OTPs
    cleanup_expired_otps()
    
    # Get the latest OTP for this user (development only)
    dev_otp = None
    if settings.DEBUG:
        latest_otp = OTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
        if latest_otp:
            dev_otp = latest_otp.otp_code
    
    context = {
        'form': form,
        'identifier': identifier,
        'identifier_type': get_identifier_type(identifier),
        'dev_otp': dev_otp,
    }
    return render(request, 'authapp/otp_verification.html', context)

@login_required
def profile_completion_view(request):
    """Profile completion view for new users"""
    # Check if user already has a profile
    if UserProfile.objects.filter(user=request.user).exists():
        messages.info(request, 'Profile already completed')
        return redirect('authapp:home')  # THIS MUST BE INSIDE THE IF BLOCK

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user profile
                    profile = form.save(commit=False)
                    profile.user = request.user
                    profile.save()
                    
                    # Update user's first_name and last_name
                    request.user.first_name = profile.first_name
                    request.user.last_name = profile.last_name
                    request.user.save()
                    
                    # Clear new user session flag
                    if 'is_new_user' in request.session:
                        del request.session['is_new_user']
                    
                    messages.success(request, f'Welcome, {profile.first_name}! Your profile has been completed.')
                    return redirect('authapp:home')
                    
            except Exception as e:
                logger.error(f"Error creating profile: {e}")
                messages.error(request, 'Error creating profile. Please try again.')
    else:
        form = ProfileCompletionForm()
    
    return render(request, 'authapp/profile_completion.html', {'form': form})

@login_required
def home_view(request):
    """Home view for authenticated users"""
    user = request.user
    
    # Get user's full name from profile
    if hasattr(user, 'profile'):
        full_name = user.profile.get_full_name()
    else:
        full_name = user.get_identifier()
    
    context = {
        'user': user,
        'full_name': full_name,
        'has_profile': hasattr(user, 'profile')
    }
    
    return render(request, 'authapp/home.html', context)

def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        # Deactivate user session
        try:
            UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key
            ).update(is_active=False)
        except Exception as e:
            logger.error(f"Error deactivating session: {e}")
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('authapp:login')

@require_http_methods(["POST"])
@csrf_exempt
def resend_otp_view(request):
    """API endpoint for resending OTP"""
    try:
        data = json.loads(request.body)
        identifier = data.get('identifier')
        
        if not identifier:
            return JsonResponse({'error': 'Identifier is required'}, status=400)
        
        # Find user
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(mobile=identifier)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
        
        # Check rate limiting (max 3 OTPs per hour)
        recent_otps = OTP.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        )
        
        if recent_otps.count() >= 3:
            return JsonResponse({'error': 'Too many OTP requests. Please wait before requesting another.'}, status=429)
        
        # Generate and send new OTP
        otp_code = generate_otp(settings.OTP_LENGTH)
        otp_instance = create_otp_instance(user, otp_code)
        
        if send_otp(identifier, otp_code):
            return JsonResponse({'message': 'OTP resent successfully'})
        else:
            otp_instance.delete()
            return JsonResponse({'error': 'Failed to send OTP'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error resending OTP: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def profile_view(request):
    """View and edit user profile"""
    user = request.user
    
    if not hasattr(user, 'profile'):
        messages.warning(request, 'Please complete your profile first')
        return redirect('authapp:profile_completion')
    
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            
            # Update user's first_name and last_name
            user.first_name = user.profile.first_name
            user.last_name = user.profile.last_name
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('authapp:profile')
    else:
        form = ProfileCompletionForm(instance=user.profile)
    
    context = {
        'form': form,
        'user': user,
        'profile': user.profile
    }
    
    return render(request, 'authapp/profile.html', context)
