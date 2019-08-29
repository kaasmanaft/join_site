from django.urls import path
from django.views.generic import ListView
from .views import db_goods_view_tmp, show_goods_by_id, save_order, show_user_orders
from .models import Order

urlpatterns = [
    path(r'all/', ListView.as_view(template_name='Order/home.html', model=Order), name='orders'),
    path(r'save/', save_order, name='save_order'),
    path(r'user/', show_user_orders, name='user_order'),
    path(r'db/<int:limit>/', db_goods_view_tmp, name='db'),
    path(r'item/<int:item_id>/', show_goods_by_id, name='item'),
              ]