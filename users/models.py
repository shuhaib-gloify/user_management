from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    author = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Library(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=100)
    published_on = models.DateField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    libraries = models.ManyToManyField(Library, related_name='books')

    def __str__(self):
        return self.name
