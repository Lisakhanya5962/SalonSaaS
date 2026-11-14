from django import forms

from employees.models import Employee

from .models import StaffAvailability


class StaffAvailabilityForm(forms.ModelForm):

    class Meta:

        model = StaffAvailability

        fields = [
            "staff",
            "day_of_week",
            "start_time",
            "end_time",
            "is_working",
        ]

        widgets = {
            "staff": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "day_of_week": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "start_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "class": "form-control",
                },
            ),

            "end_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "class": "form-control",
                },
            ),

            "is_working": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {
            "staff": "Staff Member",
            "day_of_week": "Day",
            "start_time": "Start Time",
            "end_time": "End Time",
            "is_working": "Working Day",
        }

    def __init__(
        self,
        *args,
        business=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.business = business

        if business is not None:

            employee_ids = (
                Employee.objects
                .filter(
                    business=business,
                    is_active=True,
                    membership__is_active=True,
                )
                .values_list(
                    "user_id",
                    flat=True,
                )
            )

            self.fields["staff"].queryset = (
                self.fields["staff"]
                .queryset
                .filter(
                    id__in=employee_ids,
                )
                .order_by(
                    "first_name",
                    "last_name",
                    "username",
                )
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

        staff = cleaned_data.get("staff")
        day_of_week = cleaned_data.get("day_of_week")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        is_working = cleaned_data.get("is_working")

        # ---------------------------------------------
        # WORKING HOURS VALIDATION
        # ---------------------------------------------

        if is_working:

            if not start_time:

                self.add_error(
                    "start_time",
                    "Start time is required for a working day.",
                )

            if not end_time:

                self.add_error(
                    "end_time",
                    "End time is required for a working day.",
                )

            if start_time and end_time:

                if end_time <= start_time:

                    self.add_error(
                        "end_time",
                        "End time must be later than start time.",
                    )

        # ---------------------------------------------
        # DUPLICATE SCHEDULE VALIDATION
        # ---------------------------------------------

        if (
            staff
            and day_of_week is not None
            and self.business
        ):

            existing = (
                StaffAvailability.objects
                .filter(
                    business=self.business,
                    staff=staff,
                    day_of_week=day_of_week,
                )
            )

            if self.instance.pk:

                existing = existing.exclude(
                    pk=self.instance.pk
                )

            if existing.exists():

                raise forms.ValidationError(
                    "A schedule for this staff member "
                    "and day already exists."
                )

        return cleaned_data

    def save(
        self,
        commit=True,
    ):

        instance = super().save(
            commit=False
        )

        instance.business = self.business

        if commit:

            instance.save()

        return instance