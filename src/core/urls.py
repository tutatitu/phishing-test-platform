from django.urls import path
from . import views
from .views import phishing_page, track_click

urlpatterns = [
    path("", views.home, name="home"),
    path("phishing/", phishing_page, name="phishing_page"),
    path("track/<uuid:token>/", track_click, name="track_click"),
]
