import uuid as UUID
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .forms import NewCreationForm
from django.contrib import messages
from .models import Employee
from supercustomer.models import su_additional

def customer_view(request):
    users = {'users': User.objects.filter(groups__name=request.user.username)}
    return render(request, 'customer/home.html', context=users)


def register(request, uuid):
    if request.method == "POST":
        form = NewCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            uuid = form.cleaned_data.get('uuid')
            su = su_additional.objects.filter(uuid_for_reg=uuid).first()
            group = su.user.groups.first()
            # group = su_additional.objects.filter(uuid_for_reg=uuid).first()
            user = User.objects.filter(username=username).first()
            user.groups.add(group)
            su.uuid_for_reg = UUID.uuid4()
            su.save()
            user.save()
            return redirect('customers')
        # print(request.POST.dict())
    form = NewCreationForm(
        {'username': 'User', 'email': 'user@email.by',
         'password1': 'dkskalk!a)', 'password2': 'dkskalk!a)', 'uuid': uuid}
    )
    return render(request, 'customer/register.html', {'form': form})

def dummy_register(request):
    uuid = UUID.uuid4()
    if request.method == "POST":
        form = NewCreationForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            uuid = form.cleaned_data.get('uuid')
            su = su_additional.objects.filter(uuid_for_reg=uuid).first()

            group = su.user.groups.first()
            # group = su_additional.objects.filter(uuid_for_reg=uuid).first()
            user = User.objects.filter(username=username).first()
            user.groups.add(group)
            su.uuid_for_reg = UUID.uuid4()
            su.save()
            user.save()
            return redirect('customers')
           # print(request.POST.dict())
    form = NewCreationForm(
        {'username': 'User', 'email': 'user@email.by',
         'password1': 'dkskalk!a)', 'password2': 'dkskalk!a)', 'uuid': uuid}
    )
    return render(request, 'customer/register.html', {'form': form})
