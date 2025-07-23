from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_verification_email_task_to_user(subject, message, recipient):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False
        )
    except Exception as e:
        print("Celery task failed:", str(e))


@shared_task
def send_password_reset_email_task(subject, message, recipient):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False
        )
    except Exception as e:
        print("Celery task failed (password reset):", str(e))
