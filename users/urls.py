from django.urls import path

from .views import RegisterAPIView, LoginAPIView, GetAllUsers, VerifyEmailView, PasswordResetConfirmView, \
    PasswordResetRequestView, LibraryListAPIView, LibraryBooksAPIView, BookLibrariesAPIView, AuthorBooksAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('all_users/', GetAllUsers.as_view(), name='all_users'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('request-reset-password/', PasswordResetRequestView.as_view(), name='request-reset-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    path('libraries/', LibraryListAPIView.as_view(), name='library-list'),
    path('libraries/<int:pk>/books/', LibraryBooksAPIView.as_view(), name='library-books'),
    path('books/<int:pk>/libraries/', BookLibrariesAPIView.as_view(), name='book-libraries'),
    path('authors/<int:pk>/books/', AuthorBooksAPIView.as_view(), name='author-books'),
]
