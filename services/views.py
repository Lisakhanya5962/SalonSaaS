
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import BusinessMembership

from .forms import ServiceForm
from .models import Service


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
def service_list(request):

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

    services = Service.objects.filter(
        business=business,
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:

        services = services.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    category = request.GET.get(
        "category",
        "",
    )

    if category:

        services = services.filter(
            category=category,
        )

    status = request.GET.get(
        "status",
        "active",
    )

    if status == "inactive":

        services = services.filter(
            is_active=False,
        )

    elif status == "all":

        pass

    else:

        services = services.filter(
            is_active=True,
        )

    services = services.order_by(
        "category",
        "name",
    )

    return render(
        request,
        "services/service_list.html",
        {
            "business": business,
            "membership": membership,
            "services": services,
            "search_query": search_query,
            "category": category,
            "status": status,
            "categories": Service.Category.choices,
        },
    )


@login_required
def service_create(request):

    membership = get_user_business_membership(
        request.user
    )

    if membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    if request.method == "POST":

        form = ServiceForm(
            request.POST,
        )

        if form.is_valid():

            service = form.save(
                commit=False,
            )

            service.business = membership.business

            service.save()

            messages.success(
                request,
                "Service added successfully.",
            )

            return redirect(
                "service_list",
            )

    else:

        form = ServiceForm()

    return render(
        request,
        "services/service_form.html",
        {
            "form": form,
            "business": membership.business,
            "membership": membership,
            "page_title": "Add Service",
            "submit_text": "Add Service",
        },
    )


@login_required
def service_edit(request, service_id):

    membership = get_user_business_membership(
        request.user
    )

    if membership is None:

        messages.error(
            request,
            "You are not associated with an active business.",
        )

        return redirect("dashboard")

    service = get_object_or_404(
        Service,
        id=service_id,
        business=membership.business,
    )

    if request.method == "POST":

        form = ServiceForm(
            request.POST,
            instance=service,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Service updated successfully.",
            )

            return redirect(
                "service_list",
            )

    else:

        form = ServiceForm(
            instance=service,
        )

    return render(
        request,
        "services/service_form.html",
        {
            "form": form,
            "business": membership.business,
            "membership": membership,
            "service": service,
            "page_title": "Edit Service",
            "submit_text": "Save Changes",
        },
    )


@login_required
def service_toggle_status(
    request,
    service_id,
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

    service = get_object_or_404(
        Service,
        id=service_id,
        business=membership.business,
    )

    service.is_active = not service.is_active

    service.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if service.is_active:

        messages.success(
            request,
            "Service activated successfully.",
        )

    else:

        messages.success(
            request,
            "Service deactivated successfully.",
        )

    return redirect(
        "service_list",
    )
