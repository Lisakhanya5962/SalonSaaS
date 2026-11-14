
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import BusinessMembership
from employees.models import Employee

from .forms import StaffAvailabilityForm
from .models import StaffAvailability


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


@login_required
def availability_list(request):

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

    # ---------------------------------------------------------
    # GET STAFF AVAILABILITY
    # ---------------------------------------------------------

    availability = (
        StaffAvailability.objects
        .filter(
            business=business,
        )
        .select_related("staff")
        .order_by(
            "day_of_week",
            "start_time",
            "staff__first_name",
            "staff__last_name",
        )
    )

    # ---------------------------------------------------------
    # FILTER BY EMPLOYEE
    # ---------------------------------------------------------

    staff_id = request.GET.get(
        "staff",
        "",
    )

    if staff_id:

        availability = availability.filter(
            staff_id=staff_id,
        )

    # ---------------------------------------------------------
    # FILTER BY DAY
    # ---------------------------------------------------------

    day = request.GET.get(
        "day",
        "",
    )

    if day != "":

        availability = availability.filter(
            day_of_week=day,
        )

    # ---------------------------------------------------------
    # GET EMPLOYEES FOR FILTER
    # ---------------------------------------------------------

    employees = (
        Employee.objects
        .filter(
            business=business,
            is_active=True,
            membership__is_active=True,
        )
        .select_related(
            "user",
            "membership",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
            "user__username",
        )
    )

    return render(
        request,
        "scheduling/availability_list.html",
        {
            "business": business,
            "membership": membership,
            "availability": availability,

            # Employees are now used instead of
            # BusinessMembership objects.
            "staff_members": employees,
            "employees": employees,

            "days": StaffAvailability.DayOfWeek.choices,
            "selected_staff": staff_id,
            "selected_day": day,
        },
    )


@login_required
def availability_create(request):

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

    if request.method == "POST":

        form = StaffAvailabilityForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Staff availability added successfully.",
            )

            return redirect(
                "availability_list",
            )

    else:

        form = StaffAvailabilityForm(
            business=business,
        )

    return render(
        request,
        "scheduling/availability_form.html",
        {
            "form": form,
            "business": business,
            "membership": membership,
            "page_title": "Add Staff Availability",
            "submit_text": "Save Availability",
        },
    )


@login_required
def availability_edit(
    request,
    availability_id,
):

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

    availability = get_object_or_404(
        StaffAvailability,
        id=availability_id,
        business=business,
    )

    if request.method == "POST":

        form = StaffAvailabilityForm(
            request.POST,
            instance=availability,
            business=business,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Staff availability updated successfully.",
            )

            return redirect(
                "availability_list",
            )

    else:

        form = StaffAvailabilityForm(
            instance=availability,
            business=business,
        )

    return render(
        request,
        "scheduling/availability_form.html",
        {
            "form": form,
            "business": business,
            "membership": membership,
            "availability": availability,
            "page_title": "Edit Staff Availability",
            "submit_text": "Save Changes",
        },
    )


@login_required
def availability_delete(
    request,
    availability_id,
):

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

    availability = get_object_or_404(
        StaffAvailability,
        id=availability_id,
        business=business,
    )

    if request.method == "POST":

        availability.delete()

        messages.success(
            request,
            "Staff availability deleted successfully.",
        )

        return redirect(
            "availability_list",
        )

    return render(
        request,
        "scheduling/availability_confirm_delete.html",
        {
            "availability": availability,
            "business": business,
            "membership": membership,
        },
    )
