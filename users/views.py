import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Library, Book
from .serializers import LibrarySerializer, BookDetailSerializer, AuthorBooksSerializer
from .serializers import RegisterSerializer
from .tasks import send_password_reset_email_task
from .utils import send_verification_email

logger = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        try:
            if serializer.is_valid():
                user = serializer.save()
                send_verification_email(user, request)
                return Response(
                    {"message": "Registration successful. Please check your email to activate your account."},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as db_err:
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {"error": "Something went wrong during registration."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:

            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)

            if user.is_active:
                return Response({"message": "Account is already active."}, status=status.HTTP_200_OK)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, ValueError, TypeError, OverflowError) as decode_error:
            logger.warning(f"Verification failed: {decode_error}")
            return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error during email verification: {e}")
            return Response({"error": "Something went wrong. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    return Response({"error": "Account is not activated."}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({"error": "Something went wrong during login."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_path = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = request.build_absolute_uri(reset_path)

            subject = "Reset your password"
            message = (
                f"Hi {user.username},\n\n"
                f"Click the link below to reset your password:\n\n{reset_url}\n\n"
                f"If you didn’t request this, ignore this email."
            )

            send_password_reset_email_task.delay(subject, message, user.email)

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Password reset email failed: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        new_password = request.data.get('password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, ValueError, TypeError, OverflowError) as e:
            logger.warning(f"Reset link failed: {e}")
            return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllUsers(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LibraryListAPIView(APIView):
    def get(self, request):
        try:
            libraries = Library.objects.all()
            serializer = LibrarySerializer(libraries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error fetching library list: {e}")
            return Response({'error': 'An error occurred while retrieving libraries.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LibraryBooksAPIView(APIView):
    def get(self, request, pk):
        try:
            library = get_object_or_404(Library, pk=pk)
            books = library.books.all()
            serializer = BookDetailSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error fetching books for library ID {pk}: {e}")
            return Response({'error': 'An error occurred while retrieving books for the library.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookLibrariesAPIView(APIView):
    def get(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)
            libraries = book.libraries.all()
            serializer = LibrarySerializer(libraries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error fetching libraries for book ID {pk}: {e}")
            return Response({'error': 'An error occurred while retrieving libraries for the book.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthorBooksAPIView(APIView):
    def get(self, request, pk):
        try:
            author = get_object_or_404(User, pk=pk)
            books = Book.objects.filter(author=author)
            serializer = AuthorBooksSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error fetching books for author ID {pk}: {e}")
            return Response({'error': 'An error occurred while retrieving books for the author.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
