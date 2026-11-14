
import calendar
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from businesses.models import BusinessMembership
from customers.models import Customer
from scheduling.models import StaffAvailability
from notifications.models import Notification
from notifications.utils import create_notification

from .forms import AppointmentForm
from .models import Appointment
User = get_user_model()

def get_user_business_membership(user):
    return (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )


# ============================================================
# BUSINESS / STAFF APPOINTMENTS
# ============================================================

@login_required
def appointment_list(request):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    business = membership.business

    appointments = (
        Appointment.objects
        .filter(business=business)
        .select_related(
            "customer",
            "service",
            "staff",
        )
        .order_by(
            "appointment_date",
            "start_time",
        )
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        appointments = appointments.filter(
            Q(customer__first_name__icontains=search_query)
            | Q(customer__last_name__icontains=search_query)
            | Q(service__name__icontains=search_query)
            | Q(staff__username__icontains=search_query)
            | Q(staff__first_name__icontains=search_query)
            | Q(staff__last_name__icontains=search_query)
        )

    selected_date = request.GET.get(
        "date",
        "",
    ).strip()

    if selected_date:
        try:
            date.fromisoformat(selected_date)

            appointments = appointments.filter(
                appointment_date=selected_date,
            )

        except ValueError:
            selected_date = ""

    selected_status = request.GET.get(
        "status",
        "",
    ).strip()

    valid_statuses = dict(
        Appointment.Status.choices
    )

    if selected_status not in valid_statuses:
        selected_status = ""

    if selected_status:
        appointments = appointments.filter(
            status=selected_status,
        )

    return render(
        request,
        "appointments/appointment_list.html",
        {
            "business": business,
            "membership": membership,
            "appointments": appointments,
            "search_query": search_query,
            "selected_date": selected_date,
            "selected_status": selected_status,
            "statuses": Appointment.Status.choices,
        },
    )


@login_required
def appointment_create(request):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    business = membership.business

    if request.method == "POST":

        form = AppointmentForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            form.save(
                created_by=request.user,
            )

            messages.success(
                request,
                "Appointment booked successfully.",
            )

            return redirect(
                "appointment_list"
            )

    else:

        form = AppointmentForm(
            business=business,
        )

    return render(
        request,
        "appointments/appointment_form.html",
        {
            "form": form,
            "business": business,
            "membership": membership,
            "page_title": "Book Appointment",
            "submit_text": "Book Appointment",
        },
    )


@login_required
def appointment_detail(request, appointment_id):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "business",
            "customer",
            "service",
            "staff",
            "created_by",
        ),
        id=appointment_id,
        business=membership.business,
    )

    return render(
        request,
        "appointments/appointment_detail.html",
        {
            "appointment": appointment,
            "business": membership.business,
            "membership": membership,
        },
    )


@login_required
def appointment_edit(request, appointment_id):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        business=membership.business,
    )

    if request.method == "POST":

        form = AppointmentForm(
            request.POST,
            business=membership.business,
            instance=appointment,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Appointment updated successfully.",
            )

            return redirect(
                "appointment_detail",
                appointment_id=appointment.id,
            )

    else:

        form = AppointmentForm(
            business=membership.business,
            instance=appointment,
        )

    return render(
        request,
        "appointments/appointment_form.html",
        {
            "form": form,
            "business": membership.business,
            "membership": membership,
            "appointment": appointment,
            "page_title": "Edit Appointment",
            "submit_text": "Save Changes",
        },
    )


@login_required
def appointment_status(request, appointment_id):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        business=membership.business,
    )

    if request.method != "POST":
        return redirect(
            "appointment_detail",
            appointment_id=appointment.id,
        )

    new_status = request.POST.get("status")

    valid_statuses = dict(
        Appointment.Status.choices
    )

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid appointment status.",
        )

        return redirect(
            "appointment_detail",
            appointment_id=appointment.id,
        )

    appointment.status = new_status

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Appointment marked as {valid_statuses[new_status]}.",
    )

    return redirect(
        "appointment_detail",
        appointment_id=appointment.id,
    )


@login_required
def appointment_cancel(request, appointment_id):

    membership = get_user_business_membership(request.user)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        business=membership.business,
    )

    if request.method == "POST":

        appointment.status = Appointment.Status.CANCELLED

        appointment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Appointment cancelled successfully.",
        )

    return redirect(
        "appointment_list"
    )


# ============================================================
# BUSINESS APPOINTMENT CALENDAR
# ============================================================

@login_required
def appointment_calendar(request):

    membership = get_user_business_membership(
        request.user
    )

    if membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    business = membership.business

    today = date.today()

    try:

        month = int(
            request.GET.get(
                "month",
                today.month,
            )
        )

        year = int(
            request.GET.get(
                "year",
                today.year,
            )
        )

    except (TypeError, ValueError):

        month = today.month
        year = today.year

    if month < 1:

        month = 12
        year -= 1

    elif month > 12:

        month = 1
        year += 1

    appointments = (
        Appointment.objects
        .filter(
            business=business,
            appointment_date__year=year,
            appointment_date__month=month,
        )
        .select_related(
            "customer",
            "service",
            "staff",
        )
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:

        appointments = appointments.filter(

            Q(
                customer__first_name__icontains=
                search_query
            )

            |

            Q(
                customer__last_name__icontains=
                search_query
            )

            |

            Q(
                service__name__icontains=
                search_query
            )

            |

            Q(
                staff__username__icontains=
                search_query
            )

            |

            Q(
                staff__first_name__icontains=
                search_query
            )

            |

            Q(
                staff__last_name__icontains=
                search_query
            )

        )

    staff_id = request.GET.get(
        "staff",
        "",
    )

    if staff_id:

        try:

            appointments = appointments.filter(
                staff_id=int(staff_id)
            )

        except (TypeError, ValueError):

            staff_id = ""

    status = request.GET.get(
        "status",
        "",
    )

    valid_statuses = dict(
        Appointment.Status.choices
    )

    if status not in valid_statuses:

        status = ""

    if status:

        appointments = appointments.filter(
            status=status
        )

    appointments = appointments.order_by(
        "appointment_date",
        "start_time",
    )

    appointments_by_day = {}

    for appointment in appointments:

        day = appointment.appointment_date.day

        appointments_by_day.setdefault(
            day,
            []
        ).append(
            appointment
        )

    month_calendar = calendar.Calendar(
        firstweekday=0
    )

    calendar_weeks = (
        month_calendar.monthdayscalendar(
            year,
            month,
        )
    )

    if month == 1:

        previous_month = 12
        previous_year = year - 1

    else:

        previous_month = month - 1
        previous_year = year

    if month == 12:

        next_month = 1
        next_year = year + 1

    else:

        next_month = month + 1
        next_year = year

    staff_members = (
        BusinessMembership.objects
        .filter(
            business=business,
            is_active=True,
        )
        .select_related("user")
        .order_by(
            "user__first_name",
            "user__last_name",
            "user__username",
        )
    )

    context = {

        "business": business,

        "membership": membership,

        "calendar_weeks": calendar_weeks,

        "appointments_by_day": appointments_by_day,

        "month": month,

        "year": year,

        "month_name": calendar.month_name[month],

        "previous_month": previous_month,

        "previous_year": previous_year,

        "next_month": next_month,

        "next_year": next_year,

        "today_day": today.day,

        "today_month": today.month,

        "today_year": today.year,

        "search_query": search_query,

        "selected_staff": staff_id,

        "selected_status": status,

        "staff_members": staff_members,

        "statuses": Appointment.Status.choices,

    }

    return render(
        request,
        "appointments/calendar.html",
        context,
    )

@login_required
def customer_calendar(request):

    customer = get_object_or_404(
        Customer.objects.select_related("business"),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    business = customer.business

    appointments = (
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

    return render(
        request,
        "appointments/customer_calendar.html",
        {
            "customer": customer,
            "business": business,
            "appointments": appointments,
        },
    )
# ============================================================
# CUSTOMER BOOKING
# ============================================================

@login_required
def customer_booking(request):

    customer = get_object_or_404(
        Customer.objects.select_related("business"),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    business = customer.business

    # --------------------------------------------------------
    # CREATE FORM
    # --------------------------------------------------------

    form = AppointmentForm(
        request.POST or None,
        business=business,
    )

    # --------------------------------------------------------
    # CUSTOMER
    # The customer must not be selected manually.
    # The logged-in customer is automatically assigned.
    # --------------------------------------------------------

    form.fields["customer"].required = False

    form.fields["customer"].queryset = (
        Customer.objects.filter(
            id=customer.id,
            business=business,
            is_active=True,
        )
    )

    form.initial["customer"] = customer

    # --------------------------------------------------------
    # STAFF
    # Only staff belonging to this business
    # --------------------------------------------------------

    staff_users = (
        BusinessMembership.objects
        .filter(
            business=business,
            is_active=True,
        )
        .values_list(
            "user_id",
            flat=True,
        )
    )

    form.fields["staff"].queryset = (
        form.fields["staff"]
        .queryset
        .filter(
            id__in=staff_users,
        )
        .distinct()
    )

       # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------

    if request.method == "POST":

        if form.is_valid():

            # IMPORTANT:
            # Do not save yet because customer is not coming
            # from the HTML form.
            appointment = form.save(
                commit=False,
                created_by=request.user,
            )

            # Force the logged-in customer.
            appointment.customer = customer

            # Force the customer's business.
            appointment.business = business

            # Save the appointment.
            appointment.save()

            # ========================================================
            # CREATE APPOINTMENT NOTIFICATIONS
            # ========================================================

            notification_recipients = set()

            # Notify the selected staff member.
            if appointment.staff:
                notification_recipients.add(
                    appointment.staff_id
                )

            # Notify business management and reception.
            management_roles = [
                BusinessMembership.Role.OWNER,
                BusinessMembership.Role.MANAGER,
                BusinessMembership.Role.RECEPTIONIST,
            ]

            management_user_ids = (
                BusinessMembership.objects
                .filter(
                    business=business,
                    is_active=True,
                    role__in=management_roles,
                )
                .values_list(
                    "user_id",
                    flat=True,
                )
            )

            notification_recipients.update(
                management_user_ids
            )

            # Do not notify the customer who made the booking.
            notification_recipients.discard(
                request.user.id
            )

            # Create notifications.
            recipients = User.objects.filter(
                id__in=notification_recipients
            )

            for recipient in recipients:

                create_notification(
                    recipient=recipient,
                    title="New Appointment",
                    message=(
                        f"{customer.first_name} "
                        f"{customer.last_name} "
                        f"has booked an appointment for "
                        f"{appointment.appointment_date} "
                        f"at {appointment.start_time}."
                    ),
                    notification_type=(
                        Notification.NotificationType
                        .APPOINTMENT_BOOKED
                    ),
                    appointment=appointment,
                )

            # Success message.
            messages.success(
                request,
                "Your appointment request has been submitted successfully.",
            )

            return redirect(
                "customer_dashboard",
            )

    return render(
        request,
        "appointments/customer_booking.html",
        {
            "form": form,
            "customer": customer,
            "business": business,
        },
    )
# ============================================================
# CUSTOMER AVAILABLE SLOTS
# ============================================================

@login_required
def customer_available_slots(request):

    """
    Return available appointment slots for the logged-in customer.

    The customer can only request availability for:
    - Their own active business
    - An active staff member belonging to that business
    - An active service belonging to that business
    - A valid future date

    Existing appointments are removed from the available slots.
    """

    customer = get_object_or_404(
        Customer.objects.select_related("business"),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    business = customer.business

    staff_id = request.GET.get(
        "staff",
        "",
    ).strip()

    service_id = request.GET.get(
        "service",
        "",
    ).strip()

    selected_date = request.GET.get(
        "date",
        "",
    ).strip()

    if not staff_id or not service_id or not selected_date:

        return JsonResponse(
            {
                "success": True,
                "slots": [],
                "message": (
                    "Select a staff member, service and date."
                ),
            }
        )

    try:

        selected_date = date.fromisoformat(
            selected_date
        )

    except ValueError:

        return JsonResponse(
            {
                "success": False,
                "slots": [],
                "message": "Invalid appointment date.",
            },
            status=400,
        )

    today = timezone.localtime().date()

    if selected_date < today:

        return JsonResponse(
            {
                "success": False,
                "slots": [],
                "message": (
                    "Appointments cannot be booked in the past."
                ),
            },
            status=400,
        )

    # --------------------------------------------------------
    # VERIFY STAFF BELONGS TO THIS BUSINESS
    # --------------------------------------------------------

    staff_membership = (
        BusinessMembership.objects
        .select_related("user")
        .filter(
            business=business,
            user_id=staff_id,
            is_active=True,
        )
        .first()
    )

    if staff_membership is None:

        return JsonResponse(
            {
                "success": False,
                "slots": [],
                "message": (
                    "The selected staff member is not "
                    "available for this business."
                ),
            },
            status=400,
        )

    staff = staff_membership.user

    # --------------------------------------------------------
    # VERIFY SERVICE BELONGS TO THIS BUSINESS
    # --------------------------------------------------------

    from services.models import Service

    service = (
        Service.objects
        .filter(
            id=service_id,
            business=business,
            is_active=True,
        )
        .first()
    )

    if service is None:

        return JsonResponse(
            {
                "success": False,
                "slots": [],
                "message": (
                    "The selected service is not available."
                ),
            },
            status=400,
        )

    # --------------------------------------------------------
    # GET STAFF AVAILABILITY FOR THE SELECTED DAY
    # --------------------------------------------------------

    availability = (
        StaffAvailability.objects
        .filter(
            business=business,
            staff=staff,
            day_of_week=selected_date.weekday(),
            is_working=True,
        )
        .first()
    )

    if availability is None:

        return JsonResponse(
            {
                "success": True,
                "slots": [],
                "message": (
                    "This staff member is not working "
                    "on the selected day."
                ),
            }
        )

    # --------------------------------------------------------
    # GET EXISTING APPOINTMENTS
    # --------------------------------------------------------

    existing_appointments = (
        Appointment.objects
        .filter(
            business=business,
            staff=staff,
            appointment_date=selected_date,
        )
        .exclude(
            status=Appointment.Status.CANCELLED,
        )
        .exclude(
            status=Appointment.Status.NO_SHOW,
        )
        .order_by(
            "start_time",
        )
    )

    # --------------------------------------------------------
    # SERVICE DURATION
    # --------------------------------------------------------

    duration = timedelta(
        minutes=service.duration_minutes
    )

    working_start = datetime.combine(
        selected_date,
        availability.start_time,
    )

    working_end = datetime.combine(
        selected_date,
        availability.end_time,
    )

    # --------------------------------------------------------
    # GENERATE SLOTS
    # --------------------------------------------------------

    slots = []

    current_start = working_start

    while current_start + duration <= working_end:

        current_end = current_start + duration

        slot_start_time = current_start.time()
        slot_end_time = current_end.time()

        # -----------------------------------------------
        # DON'T OFFER TIMES THAT HAVE ALREADY PASSED
        # -----------------------------------------------

        if selected_date == today:

            current_time = timezone.localtime().time()

            if slot_start_time <= current_time:

                current_start += duration

                continue

        # -----------------------------------------------
        # CHECK FOR EXISTING APPOINTMENT CONFLICT
        # -----------------------------------------------

        is_booked = False

        for appointment in existing_appointments:

            if (
                appointment.start_time < slot_end_time
                and appointment.end_time > slot_start_time
            ):

                is_booked = True

                break

        if not is_booked:

            slots.append(
                {
                    "start_time": slot_start_time.strftime(
                        "%H:%M"
                    ),
                    "end_time": slot_end_time.strftime(
                        "%H:%M"
                    ),
                    "label": (
                        f"{slot_start_time.strftime('%H:%M')}"
                        f" - "
                        f"{slot_end_time.strftime('%H:%M')}"
                    ),
                }
            )

        current_start += duration

    return JsonResponse(
        {
            "success": True,
            "slots": slots,
            "date": selected_date.isoformat(),
            "staff": staff.get_full_name()
            or staff.username,
            "service": service.name,
            "duration_minutes": service.duration_minutes,
        }
    )

@login_required
def customer_appointment_detail(request, appointment_id):

    customer = get_object_or_404(
        Customer.objects.select_related(
            "business",
            "user",
        ),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "business",
            "customer",
            "service",
            "staff",
        ),
        id=appointment_id,
        customer=customer,
        business=customer.business,
    )

    return render(
        request,
        "appointments/customer_appointment_detail.html",
        {
            "customer": customer,
            "business": customer.business,
            "appointment": appointment,
        },
    )
@login_required
def customer_appointment_cancel(request, appointment_id):

    customer = get_object_or_404(
        Customer.objects.select_related("business"),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=customer,
        business=customer.business,
    )

    if request.method != "POST":
        return redirect(
            "customer_appointment_detail",
            appointment_id=appointment.id,
        )

    if appointment.status not in [
        Appointment.Status.PENDING,
        Appointment.Status.CONFIRMED,
    ]:
        messages.error(
            request,
            "This appointment can no longer be cancelled.",
        )

        return redirect(
            "customer_appointment_detail",
            appointment_id=appointment.id,
        )

    appointment.status = Appointment.Status.CANCELLED

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Your appointment has been cancelled successfully.",
    )

    return redirect(
        "customer_appointment_detail",
        appointment_id=appointment.id,
    )