import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_sms(mobile_number, otp_code):
    """
    Send OTP via SMS
    In production, integrate with SMS service like Twilio, AWS SNS, etc.
    """
    try:
        # TODO: Integrate with actual SMS service
        # For development, just log the OTP
        logger.info(f"SMS OTP sent to {mobile_number}: {otp_code}")
        
        # Placeholder for actual SMS integration
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"Your OTP is: {otp_code}",
        #     from_=twilio_number,
        #     to=mobile_number
        # )
        
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS OTP: {e}")
        return False

def send_otp_email(email, otp_code):
    """Send OTP via email"""
    try:
        subject = "Your Login OTP"
        message = f"Your OTP is: {otp_code}\n\nThis OTP will expire in {settings.OTP_EXPIRY_MINUTES} minutes."
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Email OTP sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email OTP: {e}")
        return False

def send_otp(identifier, otp_code):
    """
    Send OTP via appropriate method based on identifier type
    """
    if '@' in identifier:  # Email
        return send_otp_email(identifier, otp_code)
    else:  # Mobile
        return send_otp_sms(identifier, otp_code)

def is_valid_mobile(mobile):
    """Validate mobile number format"""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, mobile))

def is_valid_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_identifier_type(identifier):
    """Determine if identifier is mobile or email"""
    if '@' in identifier:
        return 'email'
    else:
        return 'mobile'

def create_otp_instance(user, otp_code):
    """Create and save OTP instance"""
    from .models import OTP
    
    expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    otp = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    return otp

def cleanup_expired_otps():
    """Clean up expired OTPs"""
    from .models import OTP
    
    expired_otps = OTP.objects.filter(expires_at__lt=timezone.now())
    count = expired_otps.count()
    expired_otps.delete()
    
    if count > 0:
        logger.info(f"Cleaned up {count} expired OTPs")
    
    return count

