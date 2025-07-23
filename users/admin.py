from django.contrib import admin

from .models import UserProfile, Library, Book

admin.site.register(UserProfile)
admin.site.register(Library)
admin.site.register(Book)
