
from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.customer_list,
        name="customer_list",
    ),

    path(
        "add/",
        views.customer_create,
        name="customer_create",
    ),

    path(
        "<int:customer_id>/",
        views.customer_detail,
        name="customer_detail",
    ),

    path(
        "<int:customer_id>/edit/",
        views.customer_edit,
        name="customer_edit",
    ),

    path(
        "<int:customer_id>/toggle-status/",
        views.customer_toggle_status,
        name="customer_toggle_status",
    ),
]
