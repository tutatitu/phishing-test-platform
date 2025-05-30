from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    AddTargetsView,
    CompanyStatsView,
    DashboardView,
    EditTemplateView,
    EmailLogsView,
    SendEmailView,
    SignUpCompanyView,
    SignUpView,
    VerifyWaitView,
    phishing_page,
    track_click,
    track_email_open,
)

# Phishing
urlpatterns = [
    path("", views.home, name="home"),
    path("phishing/", phishing_page, name="phishing_page"),
    path("track-open/<uuid:token>/", track_email_open, name="track_open"),
    path("track-click/<uuid:token>/", track_click, name="track_click"),
]

# Dashboard
urlpatterns += [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/add-targets/", AddTargetsView.as_view(), name="add_targets"),
    path("dashboard/edit-template/", EditTemplateView.as_view(), name="edit_template"),
    path("dashboard/send-email/", SendEmailView.as_view(), name="send_email"),
    path("dashboard/logs/", EmailLogsView.as_view(), name="email_logs"),
    path("dashboard/stats/", CompanyStatsView.as_view(), name="company_stats"),
]

# Auth
urlpatterns += [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html", next_page="dashboard"
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("signup/company/", SignUpCompanyView.as_view(), name="signup_company"),
    path("verify_wait", VerifyWaitView.as_view(), name="verify_wait"),
]
