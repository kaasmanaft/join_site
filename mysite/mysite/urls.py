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
from django.conf import settings
from django.contrib import admin
from django.urls import include,path
from django.contrib.auth import views as auth_views
from customer.views import customer_view, register, dummy_register
from supercustomer.views import su_register
from product.views import list_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', include('Order.urls')),
    path('product/', include('product.urls')),
    path('customers/', customer_view, name='customers'),
    path('login/', auth_views.LoginView.as_view(template_name='customer/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='customer/logout.html'), name='logout'),
    path('su_register/', su_register, name='su_register'),
    path('register/<uuid:uuid>/', register, name='register_uuid'),
    path('', list_view, name='top', kwargs={'category_slug': "top"}),

]
if settings.DEBUG:
    import debug_toolbar
    debug_urs = [path('register/', dummy_register, name='register'),
                 path('__debug__/', include(debug_toolbar.urls)),
                 ]
    urlpatterns += debug_urs