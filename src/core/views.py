from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from core.forms import CompanyCreationForm, CustomUserCreationForm
from core.models import Company, EmailLog, Target
from django.views.generic import CreateView


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
        form.instance.save()
        return redirect("dashboard_home")


class AddTargetsForm(forms.Form):
    company = forms.ModelChoiceField(queryset=Company.objects.none())
    emails = forms.CharField(
        widget=forms.Textarea, help_text="Введите email'ы через запятую"
    )


@login_required
def dashboard_home(request):
    companies = Company.objects.filter(owner=request.user)
    return render(request, "dashboard_home.html", {"companies": companies})


def home(request):
    return render(request, "home.html")


@login_required
def add_targets(request):
    form = AddTargetsForm(request.POST or None)
    form.fields["company"].queryset = Company.objects.filter(owner=request.user)

    if request.method == "POST" and form.is_valid():
        company = form.cleaned_data["company"]
        emails = form.cleaned_data["emails"].split(",")
        for email in emails:
            print(email)
            Target.objects.create(email=email.strip(), company=company)
        return redirect("dashboard_home")

    return render(request, "add_targets.html", {"form": form})


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
