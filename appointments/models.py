from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from businesses.models import Business
from customers.models import Customer
from services.models import Service


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="staff_appointments",
    )

    appointment_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "appointment_date",
            "start_time",
        ]

        indexes = [
            models.Index(
                fields=[
                    "business",
                    "appointment_date",
                ]
            ),
            models.Index(
                fields=[
                    "business",
                    "status",
                ]
            ),
            models.Index(
                fields=[
                    "staff",
                    "appointment_date",
                ]
            ),
            models.Index(
                fields=[
                    "customer",
                    "appointment_date",
                ]
            ),
        ]

    def clean(self):
        errors = {}

        # End time must be after start time
        if self.start_time and self.end_time:

            if self.end_time <= self.start_time:

                errors["end_time"] = (
                    "End time must be later than start time."
                )

        # Customer must belong to the same business
        if self.customer_id and self.business_id:

            if self.customer.business_id != self.business_id:

                errors["customer"] = (
                    "This customer does not belong to this business."
                )

        # Service must belong to the same business
        if self.service_id and self.business_id:

            if self.service.business_id != self.business_id:

                errors["service"] = (
                    "This service does not belong to this business."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):

        return (
            f"{self.customer.full_name} - "
            f"{self.service.name} - "
            f"{self.appointment_date} "
            f"{self.start_time}"
        )