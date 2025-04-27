from django.contrib import admin
from .models import Campaign, ClickEvent, CoreSettings, Target

admin.site.register(CoreSettings)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    def click_count(self, obj):
        return ClickEvent.objects.filter(target__campaign=obj).count()

    list_display = ("name", "start_date", "is_active", "click_count")


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("email", "campaign", "get_tracking_link")

    def get_tracking_link(self, obj):
        return f"http://127.0.0.1:8000/track/{obj.unique_token}/"

    get_tracking_link.short_description = "LINK"


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ("target", "clicked_at")
