from django.contrib.auth.models import User
from django.db import models


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
