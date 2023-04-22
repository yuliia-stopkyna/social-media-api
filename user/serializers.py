from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import UserFollower


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollower
        fields = ("id", "user", "follower")


class UserFollowingsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = UserFollower
        fields = ("user_id", "user_full_name")


class UserFollowersSerializer(serializers.ModelSerializer):
    follower_id = serializers.IntegerField(source="follower.id", read_only=True)
    follower_full_name = serializers.CharField(
        source="follower.get_full_name", read_only=True
    )

    class Meta:
        model = UserFollower
        fields = ("follower_id", "follower_full_name")


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "bio",
            "country",
            "picture",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "bio", "country", "picture", "followers_number")


class UserReadProfileSerializer(serializers.ModelSerializer):
    followings = UserFollowingsSerializer(many=True, read_only=True)
    followers = UserFollowersSerializer(many=True, read_only=True)
    liked_posts = serializers.SlugRelatedField(many=True, source="likes", read_only=True, slug_field="id")

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "bio",
            "country",
            "picture",
            "followings",
            "followers",
            "liked_posts"
        )
