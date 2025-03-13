from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "phone_number",
            "is_email_verified",
            # "referral_code",
            "user_type",
            "preferred_language",
            "created_at",
            "updated_at",
            "password",
            "password2",
        )
        read_only_fields = ("account_balance", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data.pop("password2", None)  # Remove password2 from data

        # Generate a username from full_name
        full_name = validated_data.get("full_name", "")
        base_username = slugify(full_name.replace(" ", "_"))
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        validated_data["username"] = username

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            full_name=validated_data.get("full_name"),
            phone_number=validated_data.get("phone_number"),
            user_type=validated_data.get("user_type"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Check if the full_name is being updated.
        if "full_name" in validated_data:
            full_name = validated_data["full_name"]
            base_username = slugify(full_name.replace(" ", "_"))
            username = base_username
            counter = 1
            # Exclude the current instance from the uniqueness check.
            while (
                User.objects.filter(username=username).exclude(pk=instance.pk).exists()
            ):
                username = f"{base_username}_{counter}"
                counter += 1
            validated_data["username"] = username

        # Proceed with the normal update.
        return super().update(instance, validated_data)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    token = serializers.CharField()


class MeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "phone_number",
            "is_email_verified",
            "user_type",
            "preferred_language",
            "created_at",
            "updated_at",
            # "password",
            # "password2",
        )
        read_only_fields = ("created_at", "updated_at")
