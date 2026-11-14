from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import BusinessMembership

from .forms import CustomerForm
from .models import Customer


def get_current_membership(request):
    return (
        BusinessMembership.objects
        .select_related("business")
        .filter(
            user=request.user,
            is_active=True,
            business__is_active=True,
        )
        .first()
    )


# ============================================================
# CUSTOMER LIST
# ============================================================

@login_required
def customer_list(request):
    membership = get_current_membership(request)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    customers = (
        Customer.objects
        .filter(
            business=membership.business,
        )
        .select_related("user")
        .order_by(
            "first_name",
            "last_name",
        )
    )

    return render(
        request,
        "customers/customer_list.html",
        {
            "business": membership.business,
            "membership": membership,
            "customers": customers,
        },
    )


# ============================================================
# CREATE CUSTOMER
# ============================================================

@login_required
def customer_create(request):
    membership = get_current_membership(request)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)

            customer.business = membership.business
            customer.created_by = request.user

            customer.save()

            messages.success(
                request,
                f"{customer.full_name} was added successfully.",
            )

            return redirect("customer_list")

    else:
        form = CustomerForm()

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "business": membership.business,
            "membership": membership,
            "page_title": "Add Customer",
            "button_text": "Add Customer",
        },
    )


# ============================================================
# CUSTOMER DETAIL
# ============================================================

@login_required
def customer_detail(request, customer_id):
    membership = get_current_membership(request)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business=membership.business,
    )

    return render(
        request,
        "customers/customer_detail.html",
        {
            "customer": customer,
            "business": membership.business,
            "membership": membership,
        },
    )


# ============================================================
# EDIT CUSTOMER
# ============================================================

@login_required
def customer_edit(request, customer_id):
    membership = get_current_membership(request)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business=membership.business,
    )

    if request.method == "POST":
        form = CustomerForm(
            request.POST,
            instance=customer,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"{customer.full_name} was updated successfully.",
            )

            return redirect(
                "customer_detail",
                customer_id=customer.id,
            )

    else:
        form = CustomerForm(
            instance=customer,
        )

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "customer": customer,
            "business": membership.business,
            "membership": membership,
            "page_title": "Edit Customer",
            "button_text": "Save Changes",
        },
    )


# ============================================================
# ACTIVATE / DEACTIVATE CUSTOMER
# ============================================================

@login_required
def customer_toggle_status(request, customer_id):
    membership = get_current_membership(request)

    if membership is None:
        messages.error(
            request,
            "You are not associated with an active business.",
        )
        return redirect("dashboard")

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business=membership.business,
    )

    customer.is_active = not customer.is_active

    customer.save(
        update_fields=["is_active"]
    )

    if customer.is_active:
        status = "activated"
    else:
        status = "deactivated"

    messages.success(
        request,
        f"{customer.full_name} has been {status} successfully.",
    )

    return redirect("customer_list")