from django.contrib import admin

from .models import UserProfile, Library, Book, OTP

admin.site.register(UserProfile)
admin.site.register(Library)
admin.site.register(Book)
admin.site.register(OTP)
