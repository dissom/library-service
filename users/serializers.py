from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "is_active",
        )
        read_only_fields = (
            "id",
            "is_staff",
            "is_active",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "label": _("Password"),
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        """create user with encrypted password"""
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Update User with encrypted password"""
        password = validated_data.pop("password")
        user = super(UserSerializer, self).update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user
