from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.db import connection, transaction

from core.models import EmailLog, EmailTemplate, Target
from phishing_platform import settings


@receiver(pre_save, sender=Target)
def handle_target_creation(sender, instance, **kwargs):
    if instance.pk is None:
        try:
            template = EmailTemplate.objects.get(campaign=instance.campaign)
            subject = template.subject
            address = settings.ADDRESS
            track_open = f"{address}/track-open/{instance.unique_token}/"
            track_click = f"{address}/track-click/{instance.unique_token}/"
            body = template.body.replace("{{ track_open }}", track_open)
            body = body.replace("{{ track_click }}", track_click)
            from_email = settings.EMAIL_HOST_USER
            to_email = instance.email
            email_message = EmailMessage(subject, body, from_email, [to_email])
            email_message.content_subtype = "html"
            email_message.send()

            transaction.on_commit(
                lambda: EmailLog.objects.create(
                    email=instance.email,
                    campaign_name=instance.campaign.name,
                    event_type="SENT",
                    details="Email has been sent successfully",
                )
            )

        except Exception as e:
            email = instance.email
            campaign_name = instance.campaign.name if instance.campaign else "Unknown"

            connection.autocommit = False
            EmailLog.objects.create(
                email=email,
                campaign_name=campaign_name,
                event_type="FAILED",
                details=f"Error: {str(e)}",
            )

            connection.connection.commit()
            connection.autocommit = True

            raise Exception(f"Error: {str(e)}")
