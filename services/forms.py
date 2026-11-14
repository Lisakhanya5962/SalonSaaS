
from django import forms

from .models import Service


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service

        fields = [
            "name",
            "description",
            "category",
            "price",
            "duration_minutes",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Fade Haircut",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the service...",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "150.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "30",
                    "min": "5",
                    "step": "5",
                }
            ),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price < 0:
            raise forms.ValidationError(
                "Price cannot be negative."
            )

        return price

    def clean_duration_minutes(self):
        duration = self.cleaned_data["duration_minutes"]

        if duration <= 0:
            raise forms.ValidationError(
                "Duration must be greater than zero."
            )

        return duration
