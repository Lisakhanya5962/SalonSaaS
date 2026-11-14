from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):

        APPOINTMENT_BOOKED = (
            "APPOINTMENT_BOOKED",
            "Appointment Booked",
        )

        APPOINTMENT_CONFIRMED = (
            "APPOINTMENT_CONFIRMED",
            "Appointment Confirmed",
        )

        APPOINTMENT_CANCELLED = (
            "APPOINTMENT_CANCELLED",
            "Appointment Cancelled",
        )

        GENERAL = (
            "GENERAL",
            "General",
        )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return f"{self.recipient} - {self.title}"

# Create your models here.
