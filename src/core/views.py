from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClickEvent, Target


def home(request):
    return render(request, "home.html")


def track_click(request, token):
    target = get_object_or_404(Target, unique_token=token)
    ClickEvent.objects.create(target=target, ip_address=request.META.get("REMOTE_ADDR"))
    return redirect("phishing_page")


def phishing_page(request):
    return HttpResponse("Это фишинговая страница. Тест успешен! 🎣")
