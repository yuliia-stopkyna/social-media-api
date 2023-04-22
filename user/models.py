import os
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.get_full_name())}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile_pictures/", filename)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, blank=True, upload_to=user_image_file_path)
    country = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.get_full_name()


class UserFollower(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followings"
    )

    class Meta:
        unique_together = ("user", "follower")

    def __str__(self) -> str:
        return f"User {self.follower} follows user {self.user}"
