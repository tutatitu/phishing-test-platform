from django.urls import path
from . import views
from .views import phishing_page, track_click, track_email_open

urlpatterns = [
    path("", views.home, name="home"),
    path("phishing/", phishing_page, name="phishing_page"),
    path("track-open/<uuid:token>/", track_email_open, name="track_open"),
    path("track-click/<uuid:token>/", track_click, name="track_click"),
]
