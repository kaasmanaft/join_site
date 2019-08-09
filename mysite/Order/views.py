from typing import List, Dict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
# from .forms import OrderForm
from django.contrib.auth.models import User
from django.db import connections
from django.db.models import Sum
from django.contrib import messages
from django.db.models import  Count
def dictfetchall(cursor) -> List:
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
          ]


def get_description_by_id(it: int) -> List:
    with connections['goods'].cursor() as cursor:
        cursor.execute('SELECT id,agg_photos,base_photo_url, description,min_qty, name, price FROM item '
                       'where id=%s;',
                       [it])
        return dictfetchall(cursor)


def total_number_orders_by_id(itemid , user) :
    count = Order.objects.filter(item_id__exact=itemid, user__groups__exact=user.groups.first()).aggregate(total_order_quantity=Sum('quantity'))#, user__groups__contains=user.groups.first())#.annotate(cun=Count('item_id'))
    return count


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
def show_user_orders(request):
    orders = Order.objects.filter(user__username__exact=request.user).values_list('item_id', 'quantity')
    order_detail_list = []
    for itemid, user_order_quantity in orders:
        total_order_quantity = total_number_orders_by_id(itemid, request.user)
        order_description = get_description_by_id(itemid)
        order_description[0].update(total_order_quantity)
        order_description[0]['user_order_quantity'] = user_order_quantity
        order_detail_list += order_description
    context = {'orders': order_detail_list}
    return render(request, template_name='Order/user_page.html', context=context)

@login_required()
def save_order(request):
    if request.method == "POST":
        item = int(request.POST['id'])
        quantity = int(request.POST['quantity'])
        try:
            order = Order.objects.get(item_id__exact=item, user__username__exact=request.user)
            if quantity > 0:
                order.quantity = order.quantity + quantity
                messages.add_message(request, messages.SUCCESS, "Order has been updated")
                order.save()
                print(order)
            else:
                messages.add_message(request, messages.ERROR, "Wrong number of goods")

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
        return redirect('item', item)
    else:
        return redirect('db', 30)


def show_goods_by_id(request, id=0):
    dbd = get_description_by_id(id)
    context = {'dbd': dbd}
    if request.user:
        try:
            order = Order.objects.get(item_id__exact=int(id), user__username__exact=request.user)
            context = {'dbd': dbd, 'user_order_quantity': order.quantity}
        except Order.DoesNotExist:
            context = {'dbd': dbd, 'quantity': 1}
    return render(request, template_name='Order/db.html', context=context)
