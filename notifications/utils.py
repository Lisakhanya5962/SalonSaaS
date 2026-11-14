from .models import Notification


def create_notification(
    recipient,
    title,
    message,
    notification_type=Notification.NotificationType.GENERAL,
    appointment=None,
):
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        appointment=appointment,
    )