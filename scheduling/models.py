
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from businesses.models import Business


class StaffAvailability(models.Model):

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="staff_availability",
    )

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_availability",
    )

    day_of_week = models.PositiveSmallIntegerField(
        choices=DayOfWeek.choices,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_working = models.BooleanField(
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
            "day_of_week",
            "start_time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "business",
                    "staff",
                    "day_of_week",
                ],
                name="unique_staff_availability_per_day",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "business",
                    "staff",
                ]
            ),
            models.Index(
                fields=[
                    "business",
                    "day_of_week",
                ]
            ),
        ]

    def clean(self):

        errors = {}

        if self.start_time and self.end_time:

            if self.end_time <= self.start_time:

                errors["end_time"] = (
                    "End time must be later than start time."
                )

        if self.staff_id and self.business_id:

            from businesses.models import BusinessMembership

            membership_exists = (
                BusinessMembership.objects.filter(
                    business_id=self.business_id,
                    user_id=self.staff_id,
                    is_active=True,
                ).exists()
            )

            if not membership_exists:

                errors["staff"] = (
                    "This staff member does not belong "
                    "to this business."
                )

        if errors:

            raise ValidationError(errors)

    def __str__(self):

        day_name = self.get_day_of_week_display()

        if not self.is_working:

            return (
                f"{self.staff.username} - "
                f"{day_name} - Day Off"
            )

        return (
            f"{self.staff.username} - "
            f"{day_name} - "
            f"{self.start_time.strftime('%H:%M')} - "
            f"{self.end_time.strftime('%H:%M')}"
        )
