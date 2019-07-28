from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Employee


class NewCreationForm(UserCreationForm):
    email = forms.EmailField()
    uuid = forms.CharField(max_length=36, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'uuid']
