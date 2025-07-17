from django.urls import path
from .views import RegisterAPIView, LoginAPIView, GetAllUsers, VerifyEmailView, PasswordResetConfirmView, PasswordResetRequestView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('all_users/', GetAllUsers.as_view(), name='all_users'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('request-reset-password/', PasswordResetRequestView.as_view(), name='request-reset-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]

