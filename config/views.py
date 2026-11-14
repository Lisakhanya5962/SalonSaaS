from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from appointments.models import Appointment
from businesses.models import BusinessMembership
from customers.models import Customer
from services.models import Service

# =============================================================
# PUBLIC LANDING PAGE
# =============================================================

def landing_page(request):
    return render(
        request,
        "landing.html",
    )
@login_required
def dashboard(request):

    # =========================================================
    # CUSTOMER
    # =========================================================

    customer = (
        Customer.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )

    if customer:
        return redirect("customer_dashboard")

    # =========================================================
    # BUSINESS / STAFF
    # =========================================================

    membership = (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )

    business = membership.business if membership else None

    context = {
        "is_customer": False,
        "business": business,
        "membership": membership,
        "today_revenue": 0,
        "today_appointments_count": 0,
        "customer_count": 0,
        "service_count": 0,
        "pending_count": 0,
        "confirmed_count": 0,
        "completed_count": 0,
        "cancelled_count": 0,
        "upcoming_appointments": [],
    }

    if business:

        today = date.today()

        # =====================================================
        # APPOINTMENTS
        # =====================================================

        appointments = (
            Appointment.objects
            .filter(
                business=business
            )
        )

        # =====================================================
        # TODAY'S APPOINTMENTS
        # =====================================================

        today_appointments = (
            appointments
            .filter(
                appointment_date=today
            )
        )

        context["today_appointments_count"] = (
            today_appointments.count()
        )

        # =====================================================
        # TODAY'S REVENUE
        # =====================================================

        context["today_revenue"] = (
            today_appointments
            .aggregate(
                total=Sum("price")
            )["total"] or 0
        )

        # =====================================================
        # CUSTOMERS
        # =====================================================

        context["customer_count"] = (
            Customer.objects
            .filter(
                business=business,
                is_active=True,
            )
            .count()
        )

        # =====================================================
        # SERVICES
        # =====================================================

        context["service_count"] = (
            Service.objects
            .filter(
                business=business,
                is_active=True,
            )
            .count()
        )

        # =====================================================
        # APPOINTMENT STATUS
        # =====================================================

        context["pending_count"] = (
            appointments
            .filter(
                status=Appointment.Status.PENDING
            )
            .count()
        )

        context["confirmed_count"] = (
            appointments
            .filter(
                status=Appointment.Status.CONFIRMED
            )
            .count()
        )

        context["completed_count"] = (
            appointments
            .filter(
                status=Appointment.Status.COMPLETED
            )
            .count()
        )

        context["cancelled_count"] = (
            appointments
            .filter(
                status=Appointment.Status.CANCELLED
            )
            .count()
        )

        # =====================================================
        # UPCOMING APPOINTMENTS
        # =====================================================

        context["upcoming_appointments"] = (
            appointments
            .filter(
                appointment_date__gte=today,
            )
            .exclude(
                status__in=[
                    Appointment.Status.CANCELLED,
                    Appointment.Status.NO_SHOW,
                ]
            )
            .select_related(
                "customer",
                "service",
                "staff",
            )
            .order_by(
                "appointment_date",
                "start_time",
            )[:5]
        )

    return render(
        request,
        "dashboard.html",
        context,
    )


# =============================================================
# CUSTOMER DASHBOARD
# =============================================================

@login_required
def customer_dashboard(request):

    customer = get_object_or_404(
        Customer.objects.select_related(
            "business"
        ),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    business = customer.business

    today = date.today()

    # =========================================================
    # CUSTOMER APPOINTMENTS
    # =========================================================

    my_appointments = (
        Appointment.objects
        .filter(
            customer=customer,
            business=business,
        )
        .select_related(
            "service",
            "staff",
        )
        .order_by(
            "appointment_date",
            "start_time",
        )
    )

    # =========================================================
    # UPCOMING APPOINTMENTS
    # =========================================================

    upcoming_appointments = (
        my_appointments
        .filter(
            appointment_date__gte=today,
        )
        .exclude(
            status__in=[
                Appointment.Status.CANCELLED,
                Appointment.Status.NO_SHOW,
            ]
        )
        .order_by(
            "appointment_date",
            "start_time",
        )[:5]
    )

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        "is_customer": True,

        "customer": customer,

        "business": business,

        "my_appointments": my_appointments,

        "upcoming_appointments": upcoming_appointments,

        "my_appointment_count": (
            my_appointments.count()
        ),

        "pending_count": (
            my_appointments
            .filter(
                status=Appointment.Status.PENDING
            )
            .count()
        ),

        "confirmed_count": (
            my_appointments
            .filter(
                status=Appointment.Status.CONFIRMED
            )
            .count()
        ),

        "completed_count": (
            my_appointments
            .filter(
                status=Appointment.Status.COMPLETED
            )
            .count()
        ),

        "cancelled_count": (
            my_appointments
            .filter(
                status=Appointment.Status.CANCELLED
            )
            .count()
        ),
    }

    return render(
        request,
        "customer_dashboard.html",
        context,
    )