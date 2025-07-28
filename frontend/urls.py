from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('library/<int:pk>/<str:name>/', views.library_books, name='library_books'),
    path('book/<int:pk>/<str:name>/', views.book_libraries, name='book-libraries'),
    path('author/<int:pk>/', views.author_books, name='author_books'),
    path('book/<int:pk>/libraries/', views.book_libraries, name='book-libraries'),
    path('login/', views.user_login, name='login'),
    path('add-library/', views.add_library, name='add_library'),
    path('add-book/', views.add_book, name='add_book'),
    path('delete-library/<int:pk>/', views.delete_library, name='delete_library'),
    path('libraries/<int:id>/add-book/', views.add_book_to_library, name='add_book_to_library'),
    path('libraries/<int:pk>/books/<str:name>/', views.library_books, name='frontend/library_books'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
