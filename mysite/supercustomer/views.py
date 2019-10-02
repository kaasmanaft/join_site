from django.shortcuts import render, redirect
from .forms import SuCreationForm
from .models import su_additional
from django.contrib.auth.models import User,Group
from django.db import IntegrityError
import uuid as UUID
# Create your views here.


def su_register(request):
    if request.method == "POST":
        print(request.content_params)
        print(request.POST)
        form = SuCreationForm(request.POST)
        if form.is_valid():
            form.save()
            su_username = form.cleaned_data.get('username')
            group = Group.objects.create(name=su_username)
            user = User.objects.get_by_natural_key(username=su_username)
            user.groups.add(group)
            su_setting = su_additional(user=user, uuid_for_reg=UUID.uuid4())
            su_setting.save()
            return redirect('customers')
    form = SuCreationForm()
    return render(request, 'customer/register.html', {'form': form})