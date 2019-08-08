from django.urls import path
from django.views.generic import ListView
from .views import db_goods_view_tmp, show_goods_by_id, save_order
from .models import Order

urlpatterns = [
    path('all/', ListView.as_view(template_name='Order/home.html', model=Order), name='orders'),
    path('save/', save_order, name='save_order'),
    path('db/<int:limit>/', db_goods_view_tmp, name='db'),
    path('item/<int:id>/', show_goods_by_id, name='item'),
              ]