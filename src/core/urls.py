from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    SignUpCompanyView,
    SignUpView,
    add_targets,
    dashboard_home,
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
    path("dashboard/", dashboard_home, name="dashboard_home"),
    path("dashboard/add-targets/", add_targets, name="add_targets"),
]

# Auth
urlpatterns += [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html", next_page="dashboard_home"
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("signup/company/", SignUpCompanyView.as_view(), name="signup_company"),
]
