from rest_framework import serializers
from django.contrib.auth.models import User

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
            return user
        except Exception as e:
            raise serializers.ValidationError({"error": "Could not create user. Try again later."})
