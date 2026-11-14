
from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from businesses.models import BusinessMembership
from customers.models import Customer
from services.models import Service
from scheduling.models import StaffAvailability

from .models import Appointment


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

        fields = [
            "customer",
            "service",
            "staff",
            "appointment_date",
            "start_time",
            "notes",
        ]

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "service": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "staff": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "appointment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional appointment notes...",
                }
            ),
        }

    def __init__(
        self,
        *args,
        business=None,
        instance=None,
        **kwargs
    ):

        self.business = business

        super().__init__(
            *args,
            instance=instance,
            **kwargs,
        )

        if not business:
            raise ValueError(
                "AppointmentForm requires a business."
            )

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        self.fields["customer"].queryset = (
            Customer.objects
            .filter(
                business=business,
                is_active=True,
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

        # -------------------------------------------------
        # SERVICES
        # -------------------------------------------------

        self.fields["service"].queryset = (
            Service.objects
            .filter(
                business=business,
                is_active=True,
            )
            .order_by(
                "category",
                "name",
            )
        )

        # -------------------------------------------------
        # STAFF
        # -------------------------------------------------

        staff_memberships = (
            BusinessMembership.objects
            .filter(
                business=business,
                is_active=True,
            )
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "user__username",
            )
        )

        self.fields["staff"].queryset = (
            self.fields["staff"]
            .queryset
            .filter(
                business_memberships__business=business,
                business_memberships__is_active=True,
            )
            .distinct()
        )

        self.fields["staff"].label_from_instance = (
            self.staff_label
        )

    def staff_label(self, user):

        full_name = user.get_full_name().strip()

        if full_name:
            return f"{full_name} (@{user.username})"

        return user.username

    def clean(self):

        cleaned_data = super().clean()

        customer = cleaned_data.get("customer")
        service = cleaned_data.get("service")
        staff = cleaned_data.get("staff")
        appointment_date = cleaned_data.get(
            "appointment_date"
        )
        start_time = cleaned_data.get(
            "start_time"
        )

        # -------------------------------------------------
        # BUSINESS VALIDATION
        # -------------------------------------------------

        if customer:

            if customer.business_id != self.business.id:

                self.add_error(
                    "customer",
                    "This customer does not belong to your business.",
                )

        if service:

            if service.business_id != self.business.id:

                self.add_error(
                    "service",
                    "This service does not belong to your business.",
                )

        if staff:

            staff_is_member = (
                BusinessMembership.objects
                .filter(
                    business=self.business,
                    user=staff,
                    is_active=True,
                )
                .exists()
            )

            if not staff_is_member:

                self.add_error(
                    "staff",
                    "This staff member does not belong to your business.",
                )

        # Stop here if required information is missing.
        if not service or not staff:
            return cleaned_data

        if not appointment_date or not start_time:
            return cleaned_data

        # -------------------------------------------------
        # CALCULATE END TIME
        # -------------------------------------------------

        start_datetime = datetime.combine(
            appointment_date,
            start_time,
        )

        end_datetime = (
            start_datetime
            + timedelta(
                minutes=service.duration_minutes
            )
        )

        end_time = end_datetime.time()

        cleaned_data["calculated_end_time"] = end_time

        # -------------------------------------------------
        # PREVENT APPOINTMENTS IN THE PAST
        # -------------------------------------------------

        now = timezone.localtime()

        current_date = now.date()
        current_time = now.time().replace(
            microsecond=0
        )

        if appointment_date < current_date:

            self.add_error(
                "appointment_date",
                "Appointments cannot be booked in the past.",
            )

        elif (
            appointment_date == current_date
            and start_time <= current_time
        ):

            self.add_error(
                "start_time",
                "Appointments cannot be booked for a time that has already passed.",
            )

        # -------------------------------------------------
        # STAFF AVAILABILITY
        # -------------------------------------------------

        day_of_week = appointment_date.weekday()

        availability = (
            StaffAvailability.objects
            .filter(
                business=self.business,
                staff=staff,
                day_of_week=day_of_week,
            )
            .first()
        )

        if availability is None:

            self.add_error(
                "staff",
                "This staff member has no availability set for the selected day.",
            )

        elif not availability.is_working:

            self.add_error(
                "staff",
                "This staff member is not working on the selected day.",
            )

        else:

            # -------------------------------------------------
            # CHECK APPOINTMENT FITS INSIDE WORKING HOURS
            # -------------------------------------------------

            if start_time < availability.start_time:

                self.add_error(
                    "start_time",
                    (
                        "This appointment starts before the staff "
                        "member's working hours. Their working hours "
                        f"are {availability.start_time.strftime('%H:%M')} "
                        f"to {availability.end_time.strftime('%H:%M')}."
                    ),
                )

            if end_time > availability.end_time:

                self.add_error(
                    "start_time",
                    (
                        "This appointment ends after the staff "
                        "member's working hours. Their working hours "
                        f"are {availability.start_time.strftime('%H:%M')} "
                        f"to {availability.end_time.strftime('%H:%M')}."
                    ),
                )

        # -------------------------------------------------
        # PREVENT DOUBLE BOOKING
        # -------------------------------------------------

        overlapping_appointments = (
            Appointment.objects
            .filter(
                business=self.business,
                staff=staff,
                appointment_date=appointment_date,
            )
            .exclude(
                status=Appointment.Status.CANCELLED
            )
            .exclude(
                status=Appointment.Status.NO_SHOW
            )
        )

        # When editing an appointment, don't compare it
        # against itself.
        if self.instance and self.instance.pk:

            overlapping_appointments = (
                overlapping_appointments.exclude(
                    pk=self.instance.pk
                )
            )

        # Two appointments overlap when:
        #
        # Existing start < New end
        # AND
        # Existing end > New start

        overlapping_appointments = (
            overlapping_appointments.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
        )

        if overlapping_appointments.exists():

            conflicting_appointment = (
                overlapping_appointments
                .select_related("customer")
                .first()
            )

            self.add_error(
                "start_time",
                (
                    "This staff member already has an appointment "
                    "during this time. "
                    f"The conflicting appointment is from "
                    f"{conflicting_appointment.start_time.strftime('%H:%M')} "
                    f"to "
                    f"{conflicting_appointment.end_time.strftime('%H:%M')}."
                ),
            )

        return cleaned_data

    def save(
        self,
        commit=True,
        created_by=None,
    ):

        appointment = super().save(
            commit=False
        )

        appointment.business = self.business

        service = self.cleaned_data.get(
            "service"
        )

        if service:

            appointment.price = service.price

        appointment.end_time = self.cleaned_data[
            "calculated_end_time"
        ]

        if created_by:

            appointment.created_by = created_by

        if commit:

            appointment.save()

        return appointment
