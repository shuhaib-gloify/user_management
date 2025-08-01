import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from users.models import Library, OTP
from .forms import LibraryForm, BookForm, AddBookForm, OTPForm
from users.utils import send_otp_email, generate_otp
from django.contrib import messages
import logging

BASE_API_URL = "http://127.0.0.1:8000"

logger = logging.getLogger(__name__)


@login_required
def post_login(request):
    try:
        otp = generate_otp()
        OTP.objects.create(user=request.user, code=otp)
        send_otp_email(request.user, otp)
        logger.info(f"OTP generated and email sent to {request.user.email}")
        return redirect('verify_otp')
    except Exception as e:
        messages.error(request, "Something went wrong while generating or sending OTP.")
        logger.error(f"Error in post_login for user {request.user.username}: {e}")
        return redirect('/')


@login_required
def verify_otp(request):
    try:
        if request.method == 'POST':
            form = OTPForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['otp']
                try:
                    otp_record = OTP.objects.filter(user=request.user).latest('created_at')
                    if otp_record.code == code and not otp_record.is_expired():
                        request.session['otp_verified'] = True
                        logger.info(f"OTP verified for user {request.user.username}")
                        return redirect('/')
                    else:
                        logger.warning(f"Invalid or expired OTP attempt for user {request.user.username}")
                except OTP.DoesNotExist:
                    logger.warning(f"No OTP record found for user {request.user.username}")
            else:
                logger.warning(f"Invalid OTP form submission by user {request.user.username}")
        else:
            form = OTPForm()
    except Exception as e:
        messages.error(request, "An unexpected error occurred while verifying OTP.")
        logger.error(f"Unexpected error in verify_otp for user {request.user.username}: {e}")
        form = OTPForm()

    return render(request, 'frontend/verify_otp.html', {'form': form})

@login_required
def add_library(request):
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = LibraryForm()
    return render(request, 'frontend/add_library.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'frontend/login.html', {'error': 'Invalid username or password'})
    return render(request, 'frontend/login.html')


@staff_member_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BookForm()
    return render(request, 'frontend/add_book.html', {'form': form})


@staff_member_required
def delete_library(request, pk):
    library = get_object_or_404(Library, pk=pk)
    library.delete()
    return redirect('home')


@login_required
def add_book_to_library(request, id):
    library = get_object_or_404(Library, pk=id)

    if request.method == "POST":
        form = AddBookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            book.libraries.add(library)
        return redirect('frontend/library_books', library.id, library.name)
    else:
        form = AddBookForm()
    return render(request, 'frontend/add_book.html', {'form': form, 'library': library})


@login_required
def home(request):
    response = requests.get(f"{BASE_API_URL}/api/libraries/")
    libraries = response.json()
    is_admin = request.user.is_staff
    return render(request, 'frontend/home.html', {'libraries': libraries, 'is_admin': is_admin})


@login_required
def library_books(request, pk, name):
    response = requests.get(f"{BASE_API_URL}/api/libraries/{pk}/books/")
    books = response.json()
    return render(request, 'frontend/library_books.html', {'books': books, 'library_id': pk, 'name': name})


@login_required
def book_libraries(request, pk, name):
    response = requests.get(f"{BASE_API_URL}/api/books/{pk}/libraries/")
    libraries = response.json()
    return render(request, 'frontend/book_libraries.html', {'libraries': libraries, 'book_id': pk, 'name': name})


@login_required
def author_books(request, pk):
    response = requests.get(f"{BASE_API_URL}/api/authors/{pk}/books/")
    books = response.json()
    return render(request, 'frontend/author_books.html', {'books': books, 'author_id': pk})
