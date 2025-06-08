import csv
from celery import group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.views import View
from core.forms import (
    AddTargetsForm,
    CompanyCreationForm,
    CustomUserCreationForm,
    SendEmailForm,
)
from core.models import EmailLog, EmailTemplate, Target
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, ListView

from core.tasks import send_phishing_email_task


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "auth/signup.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("signup_company")


class SignUpCompanyView(CreateView):
    form_class = CompanyCreationForm
    template_name = "auth/signup_company.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        company = form.save()
        template = EmailTemplate.objects.create(
            company=company,
            subject="Подтверждение аккаунта",
            body="""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Обновление политики безопасности</title>
</head>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Заголовок с логотипом -->
        <header style="text-align: center; margin-bottom: 30px;">
            <img src="https://example.com/logo.png" alt="Логотип компании" style="max-width: 200px;">
            <h1 style="color: #2c3e50;">Обновление политики безопасности</h1>
        </header>
    <!-- Основной текст -->
    <div style="line-height: 1.6;">
        <p>Уважаемый сотрудник,</p>

        <p>В связи с последними изменениями в требованиях информационной безопасности,
        вам необходимо подтвердить свои учетные данные в течение 24 часов.</p>

        <p style="text-align: center; margin: 30px 0;">
            <a href="{{ track_click }}"
            style="background-color: #3498db;
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 5px;">
                Подтвердить сейчас
            </a>
        </p>

        <p>Если вы не запрашивали это обновление, проигнорируйте данное письмо.</p>
    </div>

    <!-- Подпись -->
    <footer style="margin-top: 40px;
                border-top: 1px solid #ecf0f1;
                padding-top: 20px;
                color: #7f8c8d;">
        <p>С уважением,<br>
        Отдел информационной безопасности<br>
    </p>
        <img src="{{ track_open }}"
            width="1" height="1"
            alt=""
            style="display: none;">
    </footer>
</div>
</body>
</html> """,
        )
        company.template = template
        company.save()
        return redirect("verify_wait")


class VerifyWaitView(TemplateView):
    template_name = "dashboard/verify_wait.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/base_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)


class AddTargetsView(LoginRequiredMixin, View):
    template_name = "dashboard/add_targets.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": AddTargetsForm()})

    def post(self, request, *args, **kwargs):
        company = request.user.company

        if "csv_file" in request.FILES:
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8")
            reader = csv.DictReader(decoded_file.splitlines())

            for row in reader:
                email = row.get("email")
                if email:
                    Target.objects.create(email=email.strip(), company=company)
            return redirect(self.success_url)

        if "emails" in request.POST:
            form = AddTargetsForm(request.POST)
            if form.is_valid():
                emails = form.cleaned_data["emails"]
                Target.objects.bulk_create(
                    [Target(email=email, company=company) for email in emails]
                )
                return redirect(self.success_url)
            else:
                return render(request, self.template_name, {"form": form})

        return redirect(self.success_url)


class EditTemplateView(LoginRequiredMixin, UpdateView):
    model = EmailTemplate
    template_name = "dashboard/edit_template.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        form.template = self.request.user.company.template
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user.company.template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context["template"] = company.template

        return context


class SendEmailView(LoginRequiredMixin, View):
    template_name = "dashboard/send_email.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = SendEmailForm(user=request.user)
        company = request.user.company
        return render(request, self.template_name, {"form": form, "company": company})

    def post(self, request, *args, **kwargs):
        company = request.user.company
        action = request.POST.get("action")
        selected_targets = request.POST.getlist("targets")

        if not selected_targets:
            messages.warning(request, "Select at least one target.")
            return redirect(request.path)

        if action == "delete":
            Target.objects.filter(id__in=selected_targets, company=company).delete()
            messages.success(request, "Selected targets have been deleted.")
            return redirect(request.path)

        elif action == "send":
            form = SendEmailForm(request.POST, user=request.user)
            if form.is_valid():
                targets = Target.objects.filter(
                    id__in=selected_targets, company=company
                )

                tasks = group(
                    send_phishing_email_task.s(
                        company_id=company.id, target_id=target.id
                    )
                    for target in targets
                )
                tasks.apply_async(queue="email_tasks")

                messages.success(
                    request, "Email have been sent to the selected targets."
                )
                return redirect(request.path)
        else:
            messages.error(request, "Unknown action.")
            return redirect(request.path)


class EmailLogsView(LoginRequiredMixin, ListView):
    template_name = "dashboard/email_logs.html"
    model = EmailLog
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context["logs"] = EmailLog.objects.filter(company_name=company.name).order_by(
            "-timestamp"
        )

        return context


class CompanyStatsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/company_stats.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.company.is_verified:
            return redirect("verify_wait")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context["company"] = company
        context["stats"] = {
            "sent": EmailLog.objects.filter(
                event_type="SENT", company_name=company.name
            ).count(),
            "opened": EmailLog.objects.filter(
                event_type="OPENED", company_name=company.name
            ).count(),
            "clicked": EmailLog.objects.filter(
                event_type="CLICKED", company_name=company.name
            ).count(),
            "failed": EmailLog.objects.filter(
                event_type="FAILED", company_name=company.name
            ).count(),
            "total": company.target_set.count(),
        }
        return context


def home(request):
    return render(request, "home.html")


def track_email_open(request, token):
    target = get_object_or_404(Target, unique_token=token)

    if not target.is_opened:
        target.is_opened = True
        target.opened_at = timezone.now()
        target.save()

        EmailLog.objects.create(
            email=target.email,
            company_name=target.company.name,
            event_type="OPENED",
            details=f"{target.email} opened the email",
        )

    return HttpResponse(status=200)


def track_click(request, token):
    target = get_object_or_404(Target, unique_token=token)

    if not target.is_clicked:
        target.is_clicked = True
        target.clicked_at = timezone.now()
        target.save()

        EmailLog.objects.create(
            email=target.email,
            company_name=target.company.name,
            event_type="CLICKED",
            details=f"{target.email} clicked the link",
        )

    return redirect("phishing_page")


def phishing_page(request):
    return HttpResponse("This is a phishing page. Test is successful! 🎣")
