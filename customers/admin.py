
from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "business",
        "phone",
        "email",
        "gender",
        "is_active",
        "created_at",
    )

    list_filter = (
        "business",
        "gender",
        "is_active",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
    )

    ordering = (
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
