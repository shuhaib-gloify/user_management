import requests
from django.shortcuts import render

BASE_API_URL = "http://127.0.0.1:8000"


def home(request):
    response = requests.get(f"{BASE_API_URL}/api/libraries/")
    libraries = response.json()
    return render(request, 'frontend/home.html', {'libraries': libraries})


def library_books(request, pk, name):
    response = requests.get(f"{BASE_API_URL}/api/libraries/{pk}/books/")
    books = response.json()
    return render(request, 'frontend/library_books.html', {'books': books, 'library_id': pk, 'name': name})


def book_libraries(request, pk, name):
    response = requests.get(f"{BASE_API_URL}/api/books/{pk}/libraries/")
    libraries = response.json()
    return render(request, 'frontend/book_libraries.html', {'libraries': libraries, 'book_id': pk, 'name': name})


def author_books(request, pk):
    response = requests.get(f"{BASE_API_URL}/api/authors/{pk}/books/")
    books = response.json()
    return render(request, 'frontend/author_books.html', {'books': books, 'author_id': pk})
