from django.urls import path, register_converter
from .views import list_view,list_view_tmp, product_view,search_view
from .custom_path_converter import SimaSlug
register_converter(SimaSlug, 'sima_slug')

urlpatterns = [
    path(r'category/<sima_slug:category_slug>/', list_view, name='category_view'),
    path(r'<int:product_id>/', product_view, name='product_view'),
    path(r'search/', search_view, name='search_view'),
]
