from django.contrib import admin

from phishing_platform import settings
from .models import Campaign, CoreSettings, EmailLog, EmailTemplate, Target

admin.site.register(CoreSettings)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    def failed(self, obj):
        return EmailLog.objects.filter(
            campaign_name=obj.name, event_type="FAILED"
        ).count()

    def sent(self, obj):
        return EmailLog.objects.filter(
            campaign_name=obj.name, event_type="SENT"
        ).count()

    def opened(self, obj):
        return EmailLog.objects.filter(
            campaign_name=obj.name, event_type="OPENED"
        ).count()

    def clicked(self, obj):
        return EmailLog.objects.filter(
            campaign_name=obj.name, event_type="CLICKED"
        ).count()

    list_display = (
        "name",
        "start_date",
        "is_active",
        "failed",
        "sent",
        "opened",
        "clicked",
    )


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("email", "campaign", "get_click_link", "get_open_link")
    address = settings.ADDRESS

    def get_click_link(self, obj):
        return f"{self.address}/track-click/{obj.unique_token}/"

    get_click_link.short_description = "CLICK_LINK"

    def get_open_link(self, obj):
        return f"{self.address}/track-open/{obj.unique_token}/"

    get_open_link.short_description = "OPEN_LINK"


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("subject", "campaign")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("email", "campaign_name", "event_type", "timestamp")
    list_filter = ("event_type", "campaign_name")
    search_fields = ("email", "campaign_name", "details")
    readonly_fields = ("timestamp",)

    def has_add_permission(self, request):
        return False
