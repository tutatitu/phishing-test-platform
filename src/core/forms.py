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


class AddTargetsForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)

    def clean_emails(self):
        data = self.cleaned_data["emails"]
        return [email.strip() for email in data.split(",") if email.strip()]


class SendEmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")  # noqa
        super().__init__(*args, **kwargs)
