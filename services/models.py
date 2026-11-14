
from django.db import models

from businesses.models import Business


class Service(models.Model):

    class Category(models.TextChoices):
        HAIRCUT = "HAIRCUT", "Haircut"
        HAIR = "HAIR", "Hair"
        BEAUTY = "BEAUTY", "Beauty"
        NAILS = "NAILS", "Nails"
        FACIAL = "FACIAL", "Facial"
        MASSAGE = "MASSAGE", "Massage"
        SHAVING = "SHAVING", "Shaving"
        OTHER = "OTHER", "Other"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="services",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    duration_minutes = models.PositiveIntegerField(
        default=30,
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
            "category",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "business",
                    "name",
                ],
                name="unique_service_per_business",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "business",
                    "category",
                ]
            ),
            models.Index(
                fields=[
                    "business",
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.name} - R{self.price}"

    @property
    def duration_display(self):
        hours, minutes = divmod(
            self.duration_minutes,
            60,
        )

        if hours and minutes:
            return f"{hours}h {minutes}min"

        if hours:
            return f"{hours}h"

        return f"{minutes} min"
