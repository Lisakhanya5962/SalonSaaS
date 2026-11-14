
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from businesses.models import BusinessMembership

from .forms import (
    BusinessRegistrationForm,
    StaffCreationForm,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from appointments.models import Appointment

User = get_user_model()
# ============================================================
# EMPLOYEE PERMISSIONS
# ============================================================

def can_manage_employees(membership):
    """
    Owner and Manager can:
    - View employees
    - Add employees
    - Edit employees
    - Activate employees
    - Deactivate employees
    - Remove employees

    Receptionist, Barber, Stylist and Accountant:
    - View employees only
    """

    return membership.role in [
        BusinessMembership.Role.OWNER,
        BusinessMembership.Role.MANAGER,
    ]


# ============================================================
# REGISTRATION
# ============================================================

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = BusinessRegistrationForm(request.POST)

        if form.is_valid():

            try:

                user, business = form.save()

                login(request, user)

                messages.success(
                    request,
                    f"Welcome to SalonSaaS, {user.first_name}! "
                    f"Your business '{business.name}' has been created.",
                )

                return redirect("dashboard")

            except Exception as e:

                messages.error(
                    request,
                    f"Registration failed: {e}",
                )

        else:

            messages.error(
                request,
                "Please correct the errors below.",
            )

    else:

        form = BusinessRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(
        request,
        "accounts/login.html",
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully.",
    )

    return redirect("login")


# ============================================================
# ADD EMPLOYEE
# OWNER + MANAGER
# ============================================================

@login_required
def add_staff(request):

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

    if membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    if not can_manage_employees(membership):

        messages.error(
            request,
            "You do not have permission to add employees.",
        )

        return redirect("staff_list")

    if request.method == "POST":

        form = StaffCreationForm(
            request.POST,
        )

        if form.is_valid():

            try:

                user, staff_membership = form.save(
                    membership.business
                )

                messages.success(
                    request,
                    f"{user.get_full_name()} was added successfully "
                    f"as {staff_membership.get_role_display()}.",
                )

                return redirect(
                    "staff_list",
                )

            except Exception as e:

                messages.error(
                    request,
                    f"Unable to add staff: {e}",
                )

    else:

        form = StaffCreationForm()

    return render(
        request,
        "accounts/add_staff.html",
        {
            "form": form,
            "business": membership.business,
            "membership": membership,
        },
    )


# ============================================================
# EMPLOYEE LIST
# EVERY ACTIVE MEMBER CAN VIEW
# ============================================================

@login_required
def staff_list(request):

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

    if membership is None:
        messages.error(
            request,
            "You are not associated with a business.",
        )
        return redirect("dashboard")

    can_manage_employees = membership.role in [
        BusinessMembership.Role.OWNER,
        BusinessMembership.Role.MANAGER,
    ]

    staff_memberships = (
        BusinessMembership.objects
        .select_related("user")
        .filter(
            business=membership.business,
        )
        .order_by(
            "role",
            "user__first_name",
            "user__last_name",
        )
    )

    return render(
    request,
    "accounts/staff_list.html",
    {
        "business": membership.business,
        "staff_members": staff_memberships,
        "can_manage_employees": can_manage_employees,
    },
)

# ============================================================
# EDIT EMPLOYEE
# OWNER + MANAGER
# ============================================================

@login_required
def edit_staff(
    request,
    membership_id,
):

    current_membership = (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )

    if current_membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    if not can_manage_employees(current_membership):

        messages.error(
            request,
            "You do not have permission to edit employees.",
        )

        return redirect("staff_list")

    staff_membership = (
        BusinessMembership.objects
        .select_related(
            "user",
            "business",
        )
        .filter(
            id=membership_id,
            business=current_membership.business,
        )
        .first()
    )

    if staff_membership is None:

        messages.error(
            request,
            "Staff member not found.",
        )

        return redirect("staff_list")

    # Nobody can edit the business owner.
    if staff_membership.role == BusinessMembership.Role.OWNER:

        messages.error(
            request,
            "The business owner cannot be edited as staff.",
        )

        return redirect("staff_list")

    if request.method == "POST":

        staff_membership.user.first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        staff_membership.user.last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        staff_membership.user.email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        new_role = request.POST.get(
            "role",
        )

        allowed_roles = [
            BusinessMembership.Role.MANAGER,
            BusinessMembership.Role.RECEPTIONIST,
            BusinessMembership.Role.BARBER,
            BusinessMembership.Role.STYLIST,
            BusinessMembership.Role.ACCOUNTANT,
        ]

        if new_role not in allowed_roles:

            messages.error(
                request,
                "Invalid staff role.",
            )

            return redirect(
                "edit_staff",
                membership_id=membership_id,
            )

        staff_membership.user.save()

        staff_membership.role = new_role

        staff_membership.save()

        messages.success(
            request,
            "Staff member updated successfully.",
        )

        return redirect(
            "staff_list",
        )

    return render(
        request,
        "accounts/edit_staff.html",
        {
            "staff_membership": staff_membership,
            "business": current_membership.business,
            "membership": current_membership,
            "roles": [
                BusinessMembership.Role.MANAGER,
                BusinessMembership.Role.RECEPTIONIST,
                BusinessMembership.Role.BARBER,
                BusinessMembership.Role.STYLIST,
                BusinessMembership.Role.ACCOUNTANT,
            ],
        },
    )


# ============================================================
# ACTIVATE / DEACTIVATE EMPLOYEE
# OWNER + MANAGER
# ============================================================

@login_required
def toggle_staff_status(
    request,
    membership_id,
):

    current_membership = (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )

    if current_membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    if not can_manage_employees(current_membership):

        messages.error(
            request,
            "You do not have permission to change employee status.",
        )

        return redirect("staff_list")

    staff_membership = (
        BusinessMembership.objects
        .filter(
            id=membership_id,
            business=current_membership.business,
        )
        .first()
    )

    if staff_membership is None:

        messages.error(
            request,
            "Staff member not found.",
        )

        return redirect("staff_list")

    # Owner cannot be deactivated.
    if staff_membership.role == BusinessMembership.Role.OWNER:

        messages.error(
            request,
            "The business owner cannot be deactivated.",
        )

        return redirect("staff_list")

    staff_membership.is_active = not staff_membership.is_active

    staff_membership.save(
        update_fields=[
            "is_active",
        ]
    )

    status = (
        "activated"
        if staff_membership.is_active
        else "deactivated"
    )

    messages.success(
        request,
        f"Staff member {status} successfully.",
    )

    return redirect(
        "staff_list",
    )


# ============================================================
# REMOVE EMPLOYEE
# OWNER + MANAGER
# ============================================================

@login_required
def remove_staff(request, membership_id):

    current_membership = (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )

    if current_membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    # Only Owner and Manager can remove/deactivate employees.
    if current_membership.role not in [
        BusinessMembership.Role.OWNER,
        BusinessMembership.Role.MANAGER,
    ]:
        messages.error(
            request,
            "You do not have permission to remove employees.",
        )
        return redirect("staff_list")

    staff_membership = (
        BusinessMembership.objects
        .select_related(
            "user",
            "business",
        )
        .filter(
            id=membership_id,
            business=current_membership.business,
        )
        .first()
    )

    if staff_membership is None:
        messages.error(
            request,
            "Staff member not found.",
        )
        return redirect("staff_list")

    # Never remove the business owner.
    if staff_membership.role == BusinessMembership.Role.OWNER:
        messages.error(
            request,
            "The business owner cannot be removed.",
        )
        return redirect("staff_list")

    # Deactivate the membership.
    staff_membership.is_active = False
    staff_membership.save(
        update_fields=["is_active"]
    )

    # Deactivate the Employee profile too.
    employee = getattr(
        staff_membership,
        "employee_profile",
        None,
    )

    if employee is not None:
        employee.is_active = False
        employee.save(
            update_fields=["is_active"]
        )

    messages.success(
        request,
        f"{staff_membership.user.get_full_name() or staff_membership.user.username} "
        "has been deactivated successfully.",
    )

    return redirect("staff_list")

def customer_businesses(request):

    if request.user.is_authenticated:
        return redirect("customer_dashboard")

    from businesses.models import Business

    businesses = Business.objects.filter(
        is_active=True
    ).order_by("name")

    return render(
        request,
        "accounts/customer_businesses.html",
        {
            "businesses": businesses,
        },
    )

def customer_register(request, business_id):

    if request.user.is_authenticated:
        return redirect("customer_dashboard")

    from businesses.models import Business
    from customers.models import Customer
    from customers.forms import CustomerProfileForm

    # Get the selected active business from the URL
    business = get_object_or_404(
        Business,
        id=business_id,
        is_active=True,
    )

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password_confirmation = request.POST.get(
            "password_confirmation",
            "",
        )
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not first_name or not last_name or not phone:

            messages.error(
                request,
                "Please complete all required customer fields.",
            )

        elif not username or not email or not password:

            messages.error(
                request,
                "Please complete all required account fields.",
            )

        elif password != password_confirmation:

            messages.error(
                request,
                "Passwords do not match.",
            )

        elif User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "This username is already taken.",
            )

        elif User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists.",
            )

        else:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            Customer.objects.create(
                business=business,
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                created_by=user,
            )

            login(request, user)

            messages.success(
                request,
                f"Welcome to {business.name}, {first_name}!",
            )

            return redirect("customer_dashboard")

    return render(
        request,
        "accounts/customer_register.html",
        {
            "business": business,
        },
    )

def customer_login(request):
    from customers.models import Customer

    # If already logged in, send the user to the correct dashboard.
    if request.user.is_authenticated:
        is_customer = Customer.objects.filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        ).exists()

        if is_customer:
            return redirect("customer_booking")

        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            # Only active customers belonging to active businesses
            # may use the customer portal.
            is_customer = Customer.objects.filter(
                user=user,
                is_active=True,
                business__is_active=True,
            ).exists()

            if is_customer:
                login(request, user)

                messages.success(
                    request,
                    "Welcome back! You are now logged in.",
                )

                return redirect("customer_booking")

        messages.error(
            request,
            "Invalid customer login details. Please check your username and password.",
        )

    return render(request, "accounts/customer_login.html")


    return render(
        request,
        "accounts/customer_login.html",
    )

@login_required
def customer_dashboard(request):

    from customers.models import Customer
    from appointments.models import Appointment
    from django.utils import timezone

    customer = get_object_or_404(
        Customer.objects.select_related(
            "business",
            "user",
        ),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    business = customer.business

    # ---------------------------------------------------------
    # ALL CUSTOMER APPOINTMENTS
    # ---------------------------------------------------------

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
            "-appointment_date",
            "-start_time",
        )
    )

    # ---------------------------------------------------------
    # COUNTS
    # ---------------------------------------------------------

    my_appointment_count = my_appointments.count()

    pending_count = my_appointments.filter(
        status=Appointment.Status.PENDING
    ).count()

    confirmed_count = my_appointments.filter(
        status=Appointment.Status.CONFIRMED
    ).count()

    completed_count = my_appointments.filter(
        status=Appointment.Status.COMPLETED
    ).count()

    cancelled_count = my_appointments.filter(
        status=Appointment.Status.CANCELLED
    ).count()

    # ---------------------------------------------------------
    # UPCOMING APPOINTMENTS
    # ---------------------------------------------------------

    today = timezone.localdate()

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
        )
    )

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------

    return render(
        request,
        "accounts/customer_dashboard.html",
        {
            "customer": customer,
            "business": business,

            "my_appointments": my_appointments,
            "upcoming_appointments": upcoming_appointments,

            "my_appointment_count": my_appointment_count,
            "pending_count": pending_count,
            "confirmed_count": confirmed_count,
            "completed_count": completed_count,
            "cancelled_count": cancelled_count,
        },
    )
@login_required
def customer_profile(request):

    from customers.models import Customer
    from customers.forms import CustomerProfileForm

    customer = get_object_or_404(
        Customer.objects.select_related(
            "business",
            "user",
        ),
        user=request.user,
        is_active=True,
        business__is_active=True,
    )

    if request.method == "POST":

        form = CustomerProfileForm(
            request.POST,
            instance=customer,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect(
                "customer_profile",
            )

    else:

        form = CustomerProfileForm(
            instance=customer,
        )

    return render(
        request,
        "accounts/customer_profile.html",
        {
            "customer": customer,
            "business": customer.business,
            "form": form,
        },
    )