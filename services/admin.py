
from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "business",
        "category",
        "price",
        "duration_display",
        "is_active",
        "created_at",
    )

    list_filter = (
        "business",
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "business",
        "name",
    )
