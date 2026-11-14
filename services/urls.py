
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.service_list,
        name="service_list",
    ),

    path(
        "add/",
        views.service_create,
        name="service_create",
    ),

    path(
        "<int:service_id>/edit/",
        views.service_edit,
        name="service_edit",
    ),

    path(
        "<int:service_id>/toggle-status/",
        views.service_toggle_status,
        name="service_toggle_status",
    ),
]
