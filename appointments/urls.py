
from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.appointment_list,
        name="appointment_list",
    ),

    path(
        "calendar/",
        views.appointment_calendar,
        name="appointment_calendar",
    ),

    path(
        "add/",
        views.appointment_create,
        name="appointment_create",
    ),
    path(
    "customer/book/",
    views.customer_booking,
    name="customer_booking",
),
path(
    "customer/calendar/",
    views.customer_calendar,
    name="customer_calendar",
),
path(
    "customer/available-slots/",
    views.customer_available_slots,
    name="customer_available_slots",
),
path(
    "customer/<int:appointment_id>/",
    views.customer_appointment_detail,
    name="customer_appointment_detail",
),
path(
    "customer/<int:appointment_id>/cancel/",
    views.customer_appointment_cancel,
    name="customer_appointment_cancel",
),

    path(
        "<int:appointment_id>/",
        views.appointment_detail,
        name="appointment_detail",
    ),

    path(
        "<int:appointment_id>/edit/",
        views.appointment_edit,
        name="appointment_edit",
    ),

    path(
        "<int:appointment_id>/status/",
        views.appointment_status,
        name="appointment_status",
    ),

    path(
        "<int:appointment_id>/cancel/",
        views.appointment_cancel,
        name="appointment_cancel",
    ),

]
