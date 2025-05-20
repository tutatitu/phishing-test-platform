from celery import group
from django.contrib import admin

from core.tasks import send_phishing_email_task
from phishing_platform import settings
from .models import Company, CustomUser, EmailLog, EmailTemplate, Target


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ("username", "email")


admin.site.register(CustomUser, CustomUserAdmin)


@admin.action(description="📧 Start mailing")
def start_mailing(modeladmin, request, queryset):
    for company in queryset:
        targets = company.target_set.all()
        if not targets.exists():
            continue

        tasks = group(
            send_phishing_email_task.s(company_id=company.id, target_id=target.id)
            for target in targets
        )
        tasks.apply_async(queue="email_tasks")


@admin.action(description="✅ Verify selectted companies")
def verify_companies(self, request, queryset):
    queryset.update(is_verified=True)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    actions = [start_mailing, verify_companies]

    def failed(self, obj):
        return EmailLog.objects.filter(
            company_name=obj.name, event_type="FAILED"
        ).count()

    def sent(self, obj):
        return EmailLog.objects.filter(company_name=obj.name, event_type="SENT").count()

    def opened(self, obj):
        return EmailLog.objects.filter(
            company_name=obj.name, event_type="OPENED"
        ).count()

    def clicked(self, obj):
        return EmailLog.objects.filter(
            company_name=obj.name, event_type="CLICKED"
        ).count()

    list_display = (
        "name",
        "start_date",
        "is_verified",
        "failed",
        "sent",
        "opened",
        "clicked",
    )


@admin.action(description="📧 Send email")
def send_email_to_target(modeladmin, request, queryset):
    tasks = group(
        send_phishing_email_task.s(company_id=target.company.id, target_id=target.id)
        for target in queryset
    )
    tasks.apply_async(queue="email_tasks")


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    actions = [send_email_to_target]
    list_display = ("email", "company", "get_click_link", "get_open_link")
    address = settings.ADDRESS

    def get_click_link(self, obj):
        return f"{self.address}/track-click/{obj.unique_token}/"

    get_click_link.short_description = "CLICK_LINK"

    def get_open_link(self, obj):
        return f"{self.address}/track-open/{obj.unique_token}/"

    get_open_link.short_description = "OPEN_LINK"


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("subject", "company")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("email", "company_name", "event_type", "timestamp")
    list_filter = ("event_type", "company_name")
    search_fields = ("email", "company_name", "details")
    readonly_fields = ("timestamp",)

    def has_add_permission(self, request):
        return False
