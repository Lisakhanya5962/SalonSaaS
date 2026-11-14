from django.contrib import admin

from .models import Business, BusinessMembership


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business_type",
        "owner",
        "city",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
    )

    list_filter = (
        "business_type",
        "is_active",
        "province",
    )


@admin.register(BusinessMembership)
class BusinessMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "business",
        "user",
        "role",
        "is_active",
        "created_at",
    )

    search_fields = (
        "business__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "role",
        "is_active",
    )

# Register your models here.
