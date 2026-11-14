from businesses.models import BusinessMembership


def business_context(request):
    membership = None
    business = None

    if request.user.is_authenticated:
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

        if membership:
            business = membership.business

    return {
        "current_membership": membership,
        "current_business": business,
    }