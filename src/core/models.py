import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=100, unique=True)
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    template = models.ForeignKey(
        "EmailTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"


class Target(models.Model):
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_opened = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} ({self.company.name})"


class EmailTemplate(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField(
        help_text="You can use {{ track_click }} and {{ track_open }} to add links"
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

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
    company_name = models.CharField(max_length=200, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    company_id = models.PositiveIntegerField(null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.event_type} at {self.timestamp}"
