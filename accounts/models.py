from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class PlatformRole(models.TextChoices):
        PLATFORM_ADMIN = "PLATFORM_ADMIN", "Platform Admin"
        USER = "USER", "User"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=30,
        choices=PlatformRole.choices,
        default=PlatformRole.USER,
    )

    def __str__(self):
        return self.username