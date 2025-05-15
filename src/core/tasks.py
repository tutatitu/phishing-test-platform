from celery import shared_task
from django.core.mail import EmailMessage

from core.models import Campaign, EmailLog, EmailTemplate, Target
from phishing_platform import settings


@shared_task
def send_phishing_email_task(campaign_id, target_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        target = Target.objects.get(id=target_id)
        template = EmailTemplate.objects.get(campaign=campaign)
        subject = template.subject
        address = settings.ADDRESS
        track_open = f"{address}/track-open/{target.unique_token}/"
        track_click = f"{address}/track-click/{target.unique_token}/"
        body = template.body.replace("{{ track_open }}", track_open)
        body = body.replace("{{ track_click }}", track_click)
        from_email = settings.EMAIL_HOST_USER
        to_email = target.email

        email_message = EmailMessage(subject, body, from_email, [to_email])
        email_message.content_subtype = "html"
        email_message.send()

        EmailLog.objects.create(
            email=to_email,
            campaign_name=campaign.name,
            event_type="SENT",
            details="Email has been sent successfully",
        )

    except Exception as e:
        try:
            target = Target.objects.get(id=target_id)
            campaign_name = campaign.name if campaign else "Unknown"
        except Target.DoesNotExist:
            campaign_name = "Unknown"

        EmailLog.objects.create(
            email=target.email if "target" in locals() else "unknown@example.com",
            campaign_name=campaign_name,
            event_type="FAILED",
            details=f"Error: {str(e)}",
        )

        raise
