from django.conf import settings
from django.db import models


class Business(models.Model):
    class BusinessType(models.TextChoices):
        BARBERSHOP = "BARBERSHOP", "Barbershop"
        SALON = "SALON", "Salon"
        BOTH = "BOTH", "Barbershop & Salon"

    name = models.CharField(max_length=200)

    business_type = models.CharField(
        max_length=20,
        choices=BusinessType.choices,
        default=BusinessType.BOTH,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_businesses",
    )

    email = models.EmailField(blank=True)

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    address = models.TextField(blank=True)

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    province = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        default="South Africa",
    )

    logo = models.ImageField(
        upload_to="business_logos/",
        blank=True,
        null=True,
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
        ordering = ["name"]

    def __str__(self):
        return self.name


class BusinessMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        MANAGER = "MANAGER", "Manager"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        BARBER = "BARBER", "Barber"
        STYLIST = "STYLIST", "Stylist"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_memberships",
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "user"],
                name="unique_business_user_membership",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"