from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Library, Book
from .models import UserProfile


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'published_on']


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['id', 'name', 'address', 'opening_time', 'closing_time']


class BookDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'published_on', 'author', 'author_id']


class AuthorBooksSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'published_on', 'author_username']

    def get_author_username(self, obj):
        return obj.author.username


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        username = attrs.get('username', '')
        email = attrs.get('email', '')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already registered."})

        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user, author=True)
            return user
        except Exception as e:
            raise serializers.ValidationError({"error": "Could not create user. Try again later."})
