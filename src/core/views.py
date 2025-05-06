from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import EmailLog, Target


def home(request):
    return render(request, "home.html")


def track_email_open(request, token):
    target = get_object_or_404(Target, unique_token=token)

    if not target.email_opened:
        target.email_opened = True
        target.opened_at = timezone.now()
        target.save()

        EmailLog.objects.create(
            email=target.email,
            campaign_name=target.campaign.name,
            event_type="OPENED",
            details=f"{target.email} opened the email",
        )

    return HttpResponse(status=200)


def track_click(request, token):
    target = get_object_or_404(Target, unique_token=token)

    EmailLog.objects.create(
        email=target.email,
        campaign_name=target.campaign.name,
        event_type="CLICKED",
        details=f"{target.email} clicked the link",
    )

    return redirect("phishing_page")


def phishing_page(request):
    return HttpResponse("This is a phishing page. Test is successful! 🎣")
