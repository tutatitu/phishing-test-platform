from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import Company, CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class CompanyCreationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "domain")
