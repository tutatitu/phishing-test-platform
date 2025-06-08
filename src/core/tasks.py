from celery import shared_task
from django.core.mail import EmailMessage

from core.models import Company, EmailLog, EmailTemplate, Target
from phishing_platform import settings


@shared_task
def send_phishing_email_task(company_id, target_id):
    try:
        company = Company.objects.get(id=company_id)
        target = Target.objects.get(id=target_id)
        template = EmailTemplate.objects.get(company=company)
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
            company_name=company.name,
            event_type="SENT",
            details="Email has been sent successfully",
        )

    except Exception as e:
        try:
            target = Target.objects.get(id=target_id)
            company_name = company.name if company else "Unknown"
        except Target.DoesNotExist:
            company_name = "Unknown"

        EmailLog.objects.create(
            email=target.email if "target" in locals() else "unknown@example.com",
            company_name=company_name,
            event_type="FAILED",
            details=f"Error: {str(e)}",
        )

        raise
