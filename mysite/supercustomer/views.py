from django.shortcuts import render, redirect
from .forms import SuCreationForm
from .models import su_additional
from django.contrib.auth.models import User,Group
from django.db import IntegrityError
import uuid as UUID
# Create your views here.


def su_register(request):
    if request.method == "POST":
        form = SuCreationForm(request.POST)
        # print(form)
        if form.is_valid():
            form.save()
            su_username = form.cleaned_data.get('username')
            group_name = su_username
            try:
                group = Group.objects.create(name=group_name)
            except IntegrityError as exc:
                group_name = group_name+'_s'
                group = Group.objects.create(name=group_name)
                print(f"{exc.args} <--------------------------------------------------")
            user = User.objects.get_by_natural_key(username=su_username)
            user.groups.add(Group.objects.get_by_natural_key(name=group_name))
            su_setting = su_additional(user=user,uuid_for_reg=UUID.uuid4())
            su_setting.save()
            return redirect('customers')
        # print(request.POST.dict())
    form = SuCreationForm()
    return render(request, 'customer/register.html', {'form': form})