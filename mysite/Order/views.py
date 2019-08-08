from typing import List, Dict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
# from .forms import OrderForm
from django.contrib.auth.models import User
from django.db import connections


def dictfetchall(cursor) -> List:
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
          ]


def db_goods_view_tmp(request, limit=10):
    if request.method == "POST":
        print(request.user)
        print(request.body)
        return redirect('customers')
    else:
        with connections['goods'].cursor() as cursor:
            cursor.execute('SELECT id,agg_photos,base_photo_url, description,min_qty, name, price FROM item '
                           'where agg_photos is not null LIMIT %s;',
                           [limit])
            dbd = dictfetchall(cursor)

            return render(request, template_name='Order/db.html', context={'dbd': dbd})


def get_item_info(item_id: int) -> Dict:
    with connections['goods'].cursor() as cursor:
        cursor.execute('SELECT  price, is_remote_store  FROM item where id=%s;',
                       [item_id])
        item_info = dictfetchall(cursor)
        cursor.close()
    return item_info[0]


@login_required()
def save_order(request):
    if request.method == "POST":
        item = request.POST['id']
        try:
            order = Order.objects.get(item_id__exact=int(item), user__username__exact=request.user)
            print(order)

        except Order.DoesNotExist:
            print('There is no any orders with that ID')
            new_order = Order()
            new_order.item_id = request.POST['id']
            item_info = get_item_info(new_order.item_id)
            new_order.user = request.user
            new_order.quantity = request.POST['quantity']
            new_order.price = item_info['price']
            new_order.is_partner_goods = item_info['is_remote_store']
            if new_order.is_valid():
                new_order.save()
                return redirect('db', 30)
            else:
                print(repr(new_order))
                return redirect('item', new_order.item_id)
        return redirect('db', 30)
    else:
        return redirect('db', 30)


def show_goods_by_id(request, id=0):
    with connections['goods'].cursor() as cursor:
        cursor.execute("SELECT id,agg_photos,base_photo_url, description,min_qty, name, price FROM item WHERE id=%s;",
                       [id])
        dbd = dictfetchall(cursor)
        return render(request, template_name='Order/db.html', context={'dbd': dbd, 'quantity': 1})
