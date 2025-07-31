import logging

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import random
from .tasks import send_verification_email_task_to_user, send_otp_email_to_user

logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user, otp):
    subject = "Your OTP Code"
    message = (
        f"Hi {user.username},\n\n"
        f"Your OTP code is: {otp}\n\n"
        f"This code is valid for 10 minutes.\n"
    )
    send_otp_email_to_user.delay(subject, message,user.email)

def send_verification_email(user, request):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_path = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
        verification_url = request.build_absolute_uri(activation_path)

        subject = "Activate your account"
        message = (
            f"Hi {user.username},\n\n"
            f"Please click the link below to activate your account:\n\n"
            f"{verification_url}\n\n"
            f"If you did not request this, just ignore this email."
        )

        send_verification_email_task_to_user.delay(subject, message, user.email)

        print("finished send_verification_email() called")


    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
