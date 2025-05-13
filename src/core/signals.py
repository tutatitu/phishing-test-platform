from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection

from core.models import EmailLog, EmailTemplate, Target
from core.tasks import send_phishing_email_task
from phishing_platform import settings


@receiver(post_save, sender=Target)
def handle_target_creation(sender, instance, created, **kwargs):
    if created:
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
            send_phishing_email_task.delay(
                subject, body, from_email, to_email, target_id=instance.id
            )

        except Exception as e:
            connection.autocommit = False
            EmailLog.objects.create(
                email=instance.email,
                campaign_name=instance.campaign.name
                if instance.campaign
                else "Unknown",
                event_type="FAILED",
                details=f"Template error: {str(e)}",
            )
            connection.connection.commit()
            connection.autocommit = True

            instance.delete()
            raise Exception(f"Error: {str(e)}")
