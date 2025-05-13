from celery import shared_task
from django.core.mail import EmailMessage
from django.db import transaction

from core.models import EmailLog, Target


@shared_task
def send_phishing_email_task(subject, body, from_email, to_email, target_id):
    try:
        email_message = EmailMessage(subject, body, from_email, [to_email])
        email_message.content_subtype = "html"
        email_message.send()

        with transaction.atomic():
            target = Target.objects.get(id=target_id)
            EmailLog.objects.create(
                email=target.email,
                campaign_name=target.campaign.name,
                event_type="SENT",
                details="Email has been sent successfully",
            )

    except Exception as e:
        try:
            target = Target.objects.get(id=target_id)
            campaign_name = target.campaign.name if target.campaign else "Unknown"
        except Target.DoesNotExist:
            campaign_name = "Unknown"

        with transaction.atomic():
            EmailLog.objects.create(
                email=target.email if "target" in locals() else "unknown@example.com",
                campaign_name=campaign_name,
                event_type="FAILED",
                details=f"Error: {str(e)}",
            )

        if "target" in locals():
            target.delete()

        raise
