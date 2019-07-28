from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,Group,GroupManager
from django import forms
from django.db import models



class SuCreationForm(UserCreationForm):
    email = forms.EmailField()
    group = models.ManyToManyField(Group)
    # is_super_user = forms.CheckboxInput()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','is_staff']
