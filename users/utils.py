from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

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

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
