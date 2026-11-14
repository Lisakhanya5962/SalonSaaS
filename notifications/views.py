from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):

    notifications = (
        Notification.objects
        .filter(
            recipient=request.user,
        )
        .select_related(
            "appointment",
        )
        .order_by(
            "-created_at",
        )
    )

    unread_count = notifications.filter(
        is_read=False,
    ).count()

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def notification_mark_read(
    request,
    notification_id,
):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification.is_read = True

    notification.save(
        update_fields=[
            "is_read",
        ]
    )

    if notification.appointment:
        return redirect(
            "appointment_detail",
            appointment_id=notification.appointment.id,
        )

    return redirect(
        "notifications:list",
    )


@login_required
def notification_mark_all_read(request):

    if request.method == "POST":

        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True,
        )

    return redirect(
        "notifications:list",
    )