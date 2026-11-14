
from django.contrib import admin
from django.urls import include, path

from config.views import dashboard, customer_dashboard, landing_page


urlpatterns = [
    path("admin/", admin.site.urls),

    # Public landing page
    path("", landing_page, name="home"),

    # Business and staff dashboard
    path("dashboard/", dashboard, name="dashboard"),

    # Customer dashboard
    path(
        "customer/dashboard/",
        customer_dashboard,
        name="customer_dashboard",
    ),

    # Application routes
    path("accounts/", include("accounts.urls")),
    path("customers/", include("customers.urls")),
    path("services/", include("services.urls")),
    path("appointments/", include("appointments.urls")),
    path("notifications/", include("notifications.urls")),
    path("scheduling/", include("scheduling.urls")),
]
