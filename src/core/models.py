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

    def __str__(self):
        return f"{self.email} ({self.campaign.name})"


class ClickEvent(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
