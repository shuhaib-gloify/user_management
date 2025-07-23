from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('library/<int:pk>/<str:name>/', views.library_books, name='library_books'),
    path('book/<int:pk>/<str:name>/', views.book_libraries, name='book-libraries'),
    path('author/<int:pk>/', views.author_books, name='author_books'),
    path('book/<int:pk>/libraries/', views.book_libraries, name='book-libraries'),

]
