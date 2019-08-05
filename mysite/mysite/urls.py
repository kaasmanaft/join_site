"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import ListView
from customer.views import customer_view, register, dummy_register
from supercustomer.views import su_register
from Order.models import Order
from Order.views import db_goods_view_tmp, show_goods_by_id, save_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', ListView.as_view(template_name='Order/home.html', model=Order), name='orders'),
    path('order/', save_order, name='save_order'),
    path('customers/', customer_view, name='customers'),
    path('register/', dummy_register, name='register'),
    path('db/<int:limit>/', db_goods_view_tmp, name='db'),
    path('item/<int:id>/', show_goods_by_id, name='item'),
    path('login/', auth_views.LoginView.as_view(template_name='customer/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='customer/logout.html'), name='logout'),
    path('su_register/', su_register, name='su_register'),
    path('register/<uuid:uuid>', register, name='register_uuid'),
]
