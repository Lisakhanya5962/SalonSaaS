from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.availability_list,
        name="availability_list",
    ),

    path(
        "add/",
        views.availability_create,
        name="availability_create",
    ),

    path(
        "<int:availability_id>/edit/",
        views.availability_edit,
        name="availability_edit",
    ),

    path(
        "<int:availability_id>/delete/",
        views.availability_delete,
        name="availability_delete",
    ),

]