import uuid
from django.db import models


class CoreSettings(models.Model):
    site_name = models.CharField(max_length=100)
    maintenance_mode = models.BooleanField(default=False)


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Target(models.Model):
    email = models.EmailField(unique=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} ({self.campaign.name})"


class EmailTemplate(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField(
        help_text="You can use {{ track_click }} and {{ track_open }} to add links"
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject


class EmailLog(models.Model):
    EVENT_TYPES = [
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
        ("OPENED", "Opened"),
        ("CLICKED", "Clicked"),
    ]

    email = models.EmailField(null=True, blank=True)
    campaign_name = models.CharField(max_length=200, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    campaign_id = models.PositiveIntegerField(null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.event_type} at {self.timestamp}"
