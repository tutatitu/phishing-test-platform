from django.contrib import admin

from phishing_platform import settings
from .models import Campaign, ClickEvent, CoreSettings, EmailTemplate, Target

admin.site.register(CoreSettings)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    def click_count(self, obj):
        return ClickEvent.objects.filter(target__campaign=obj).count()

    list_display = ("name", "start_date", "is_active", "click_count")


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


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ("target", "clicked_at")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("subject", "campaign")
