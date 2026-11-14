from django.urls import path

from . import views


urlpatterns = [
    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "staff/",
        views.staff_list,
        name="staff_list",
    ),

    path(
        "staff/add/",
        views.add_staff,
        name="add_staff",
    ),
    path(
    "staff/<int:membership_id>/edit/",
    views.edit_staff,
    name="edit_staff",
),

path(
    "staff/<int:membership_id>/toggle/",
    views.toggle_staff_status,
    name="toggle_staff_status",
),

path(
    "staff/<int:membership_id>/remove/",
    views.remove_staff,
    name="remove_staff",
),
path(
    "customer/businesses/",
    views.customer_businesses,
    name="customer_businesses",
),
 path(
    "customer/register/<int:business_id>/",
    views.customer_register,
    name="customer_register",
),

path(
    "customer/login/",
    views.customer_login,
    name="customer_login",
),

path(
    "customer/dashboard/",
    views.customer_dashboard,
    name="customer_dashboard",
),
path(
    "customer/profile/",
    views.customer_profile,
    name="customer_profile",
),
]