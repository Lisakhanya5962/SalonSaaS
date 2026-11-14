from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from businesses.models import Business, BusinessMembership


class Employee(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    membership = models.OneToOneField(
        BusinessMembership,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    employee_id = models.CharField(
        max_length=50,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    position = models.CharField(
        max_length=100,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __str__(self):
        return (
            f"{self.user.get_full_name() or self.user.username} "
            f"- {self.business.name}"
        )