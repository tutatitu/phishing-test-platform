from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.db.models.signals import post_save

from core.models import EmailTemplate, Target
from phishing_platform import settings


@receiver(post_save, sender=Target)
def send_phishing_email(sender, instance, created, **kwargs):
    if created:
        template = EmailTemplate.objects.get(campaign=instance.campaign)
        subject = template.subject
        tracking_link = f"http://127.0.0.1:8000/track/{instance.unique_token}/"
        body = template.body.replace("{{ tracking_link }}", tracking_link)
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email
        email = EmailMessage(
            subject,
            body,
            from_email,
            [to_email],
        )
        email.content_subtype = "html"
        email.send()
